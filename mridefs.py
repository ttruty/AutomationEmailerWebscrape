import datetime, time, mridetails, io, os, collections, re
from tkinter import *
from selenium import webdriver

def driver_open():
    global DRIVER
    chromedrive ='phantomjs\\phantomjs.exe'
    DRIVER = webdriver.PhantomJS(chromedrive)

def driver_close():
    DRIVER.quit()
    
################### LOGIN GUI ###############################
class LoginFrame():
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        info_frame = Frame(master)
        info_frame.pack()

        self.info_label = Label(info_frame, text="Automation MRI Emailer\n\n Generate an email for car orders\n"
                                            "for the MRI studiy scans for next week")
        self.info_label.grid(row=0)

        self.label_1 = Label(frame, text="Username")
        self.label_2 = Label(frame, text="Password")

        self.entry_1 = Entry(frame)
        self.entry_2 = Entry(frame, show="*")

        #self.info_label.grid(row=0)
        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)

        self.logbtn = Button(frame, text="Login", command=self._login_btn_clickked)
        #elf.logbtn.bind('<Button-1>', lambda e:self._login_btn_clickked())
        master.bind('<Return>', lambda e:self._login_btn_clickked())
        self.logbtn.grid(columnspan=2)

    def _login_btn_clickked(self):
        #print("Clicked")
        global username_gui, password_gui, root
        username_gui = self.entry_1.get()
        password_gui = self.entry_2.get()
        #print(username_gui)
        root.destroy()

def login_gui():
    global root
    root = Tk()
    root.title('RADC LOGIN')
    root.geometry("350x300")
    LoginFrame(root)
    root.mainloop()

class mri_driver():
    def __init__(self):
        
        self.list_link = [] # holds the urls of staff/days
        self.logged_in = False

        self.next_week_url_list = []
        self.mri_dict = {}
        self.scan_dict = {}
        self.mri_full_list =[]
        self.mri_scan_list = []
        self.next_monday = ''

    def login(self):
        # logs into webpage
        # will only run once when called in program, once runned logged_in == True
        while self.logged_in == False:
            # Select the Username and Password
            # us, pw = login_gui()
            username = DRIVER.find_elements_by_xpath('//*[@id="j_username"]')[0]
            username.send_keys(username_gui)
            password = DRIVER.find_elements_by_xpath('//*[@id="j_password"]')[0]
            password.send_keys(password_gui)
            # Submit the form
            login_button = DRIVER.find_element_by_xpath('//*[@id="submit"]')
            login_button.click()
            self.logged_in = True

    def part_info(self, part_url):
            # this pulls the name, address, phone number from the participant summary page
            DRIVER.get(part_url)
            time.sleep(1) # thsi seems to fix the problem of overrunning webpages
            try:
                web_elem_name = DRIVER.find_elements_by_xpath('//*[@id="header_table"]/tbody/tr[1]/td[1]')
                part_name = web_elem_name[0].text
                #print(part_name)
                part_name = self.clean_part_name(part_name)
                web_elem_address = DRIVER.find_elements_by_xpath('//*[@id="overview"]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr[3]/td')
                part_address = web_elem_address[0].text
                web_elem_phone = DRIVER.find_elements_by_xpath('//*[@id="overview"]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr[4]/td')
                part_phone = web_elem_phone[0].text
                part_info = mridetails.ParticipantDetails(part_name, part_address, part_phone)
            except:
                #print("error in part info")
                part_info = mridetails.ParticipantDetails(" Error", "Error", "Error")
            return part_info

    def get_scan_info(self, url):
        # this pulls the scan info from the daily schedule page
        part_links = []
        scan_obj = []
        part_obj = []
        new_part_obj = []
        id_list = []
        valid_links = []

        # driver behind opening pages and getting data
        DRIVER.get(url)
        time.sleep(1) # thsi seems to fix the problem of overrunning webpages
        self.login() # this should only run once
        
        staff_id = (url[-3:])

        page_details = DRIVER.find_elements_by_xpath("/html/body/div[2]/table/tbody/tr")

        for elem in page_details:
            #print(elem.text)
            if 'Neuro-Imaging - MRI Scan' in elem.text:
##                print(elem.text)
                elemlines = elem.text.splitlines()
                # each list is 10 items..
                # NEED TO - refine this algorythom to find scan stuff.
                match = re.compile('\d{8}')
                id_list.append(match.findall(elemlines[0]))
                scan_site_obj = (elemlines[7])
                appt =  (elemlines[8])
                scan_time_obj = (elemlines[5])
                scan_info = mridetails.ScanDetails(scan_time_obj, scan_site_obj, appt, staff_id)
                scan_obj.append(scan_info)
                links = DRIVER.find_elements_by_xpath("//a[@href]")
                for link in links:
                    if 'participant/summary' in link.get_attribute("href") and link.get_attribute("href") not in part_links:
                        valid_links.append(link.get_attribute("href"))

        if id_list != []:
            for proj_id in id_list:
                created_link = 'https://radc.rush.edu/radc/participant/summary.htm?projid=' + proj_id[0]
                if created_link in valid_links:
                    part_links.append(created_link)
        for url in part_links:
            part_obj.append(self.part_info(url)) # creates list of all the scans that day
        new_part_obj = self.check_same_addr(part_obj)
        #print(new_part_obj)
        return scan_obj, new_part_obj


    def check_same_addr(self, object_list):
        # checks to see if the address is the object list input is repeated
        combine_name = []
        new_part_list = []
        isduplicate = False
        if len(object_list) > 1:
            for i in object_list:
                if isduplicate:
                    break
                #print(i.name)
                found =[x for x in object_list if x.address.lower() == i.address.lower()]
                if len(found) > 1:
                    
                    combine_name.append(i.name)
                    #print("This is a duplicate")
                    #str1 = ' and '.join(new_key_list)
                    if len(found) > 1 and len(combine_name) > 1:
                        combine_address = i.address
                        combine_phone = i.phone
                        combine_obj = mridetails.ParticipantDetails(' and '.join(combine_name), combine_address, combine_phone)
                        new_part_list.append(combine_obj)
                        isduplicate = True
                #print(' and '.join(combine_name), combine_address, combine_phone)
                else:
                    new_part_list.append(i)
        else:
            for i in object_list:
                new_part_list.append(i)
        return new_part_list, isduplicate
                
                      
    def next_weekday(self, d, weekday):
        # returns next week day
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0: # Target day already happened this week
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)

    def make_url(self, staff_ids):
        # returns a list of all the urls for staff daily schedule of next week
        # now = datetime.datetime(2018, 4, 20, 18, 00) # this is used to test different weeks
        now = datetime.datetime.now()
        d = datetime.date(now.year, now.month, now.day)
        self.next_monday = self.next_weekday(d, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
        #print('Next Monday is:    ' + str(next_monday))
        

        # format next monday to be used in RADC WEBPAGE
        next_monday_year = str(self.next_monday)[:4]
        next_monday_month = str(self.next_monday)[5:7]
        next_monday_day = str(self.next_monday)[8:10]

        # url for staff MONDAY schedule of NEXT week
        for ids in staff_ids:
            baseURL = 'https://radc.rush.edu/radc/schedule/staffDailySchedule.htm?'
            staffURL = baseURL + '&month=' + next_monday_month + '&year=' + next_monday_year + '&day=' + next_monday_day + '&intid=' + ids

        # look at each webpage for each DAY OF THE WEEK FOR CURRENT STAFF/WEEK
            for i in range(7):
                next_day = int(next_monday_day) + i
                if i == 0:
                    day = 'Monday'
                elif i == 1:
                    day = 'Tuesday'
                elif i == 2:
                    day = 'Wednesday'
                elif i == 3:
                    day = 'Thursday'
                elif i == 4:
                    day = 'Friday'
                elif i == 5:
                    day = 'Saturday'
                elif i == 6:
                    day = 'Sunday'
                # Prints URL for all days in week
                weekday = (self.next_weekday(d, i))
                next_week_url = baseURL + '&month=' + next_monday_month + '&year=' + next_monday_year + '&day=' + str(next_day) + '&intid=' + ids
                print(next_week_url)
                #get_scan_info(next_week_url)
                self.next_week_url_list.append(next_week_url)
        for url in self.next_week_url_list:
            daily_list = []
            self.mri_full_list.append(self.get_scan_info(url))     
        return self.mri_full_list, self.next_week_url_list, self.next_monday

    def timeConvert(self, time):
        ''' enter time in hh:mm format'''
        miliTime = time
        hours, minutes = miliTime.split(":")
        hours, minutes = int(hours), int(minutes)
        setting = "AM"
        if hours == 12:
            setting = " PM"
        if hours > 12:
            setting = " PM"
            hours -= 12
        return(("%02d:%02d" + setting) % (hours, minutes))

    def order_time(self, time):
        ''' time is in this format : Thu 10/13/2016 3:00 PM - 4:15 PM '''   
        time_list = time.split()[1:]
        print(time_list)
        # after split: ['Thu', '10/13/2016', '3:00', 'PM', '-', '4:15', 'PM']
        day = time_list[0] # 'Thu'
        
        date = time_list[1]  # '10/13/2016'
        date_split = date.split('/') # ['10', '13', '2016']
        year = int(date_split[2])
        daydate = int(date_split[1])
        month = int(date_split[0])

        start = time_list[2].split(':') # '3:00'
        start_hour = int(start[0])
        start_min = int(start[1])
        start_ampm = time_list[3] # 'PM'
        
        finish = time_list[5].split(':') # '4:15'
        stop_hour = int(finish[0])
        stop_min = int(finish[1])
        stop_ampm = time_list[6] # 'PM'
        # how to subtract 30 minutes from start time to make drop off time
        # Thu 10/13/2016 3:00 PM - 4:15 PM
        # datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
        if start_ampm == 'PM' and start_hour != 12:
            start_hour = start_hour + 12
        if stop_ampm == 'PM' and stop_hour != 12:
            stop_hour = stop_hour + 12
        scanstart_datetime_object = datetime.datetime(year, month, daydate, start_hour, start_min, 0, 0)
        scanstop_datetime_object = datetime.datetime(year, month, daydate, stop_hour, stop_min, 0, 0)
        time_change = scanstart_datetime_object - datetime.timedelta(minutes=30)
        drop_off = time_change.time()
        drop_off_hour = drop_off.hour
        drop_off_minute = drop_off.minute
        drop_off_military = str(drop_off_hour) + ':' + str(drop_off_minute)
        drop_off_time = self.timeConvert(drop_off_military)

        pick_up = scanstop_datetime_object.time()
        pick_up_hour = pick_up.hour
        pick_up_minute = pick_up.minute
        if pick_up_minute == 0:
            pick_up_minute = "00"
        pickup_military  = str(pick_up_hour) + ':' + str(pick_up_minute)
        pickup_time = self.timeConvert(pickup_military)
        
        order_times = mridetails.OrderTimes(drop_off_time, pickup_time)
        return order_times

    def order_time_2(self, time1, time2):
        ''' ONLY USED WHEN 2 SCANS'''
        ''' time is in this format : Thu 10/13/2016 3:00 PM - 4:15 PM '''   
        time1_list = time1.split()[1:]
        time2_list = time2.split()[1:]
        # after split: ['Thu', '10/13/2016', '3:00', 'PM', '-', '4:15', 'PM']
        day = time1_list[0] # 'Thu'
        
        date = time1_list[1]  # '10/13/2016'
        date_split = date.split('/') # ['10', '13', '2016']
        year = int(date_split[2])
        daydate = int(date_split[1])
        month = int(date_split[0])

        start = time1_list[2].split(':') # '3:00'
        start_hour = int(start[0])
        start_min = int(start[1])
        start_ampm = time1_list[3] # 'PM'

        finish = time2_list[5].split(':') # '4:15'
        stop_hour = int(finish[0])
        stop_min = int(finish[1])
        stop_ampm = time2_list[6] # 'PM'
        # how to subtract 30 minutes from start time to make drop off time
        # Thu 10/13/2016 3:00 PM - 4:15 PM
        # datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
        if start_ampm == 'PM' and start_hour != 12:
            start_hour = start_hour + 12
        if stop_ampm == 'PM' and stop_hour != 12:
            stop_hour = stop_hour + 12
        scanstart_datetime_object = datetime.datetime(year, month, daydate, start_hour, start_min, 0, 0)
        scanstop_datetime_object = datetime.datetime(year, month, daydate, stop_hour, stop_min, 0, 0)
        time_change = scanstart_datetime_object - datetime.timedelta(minutes=30)
        drop_off = time_change.time()
        drop_off_hour = drop_off.hour
        drop_off_minute = drop_off.minute
        drop_off_military = str(drop_off_hour) + ':' + str(drop_off_minute)
        drop_off_time = self.timeConvert(drop_off_military)

        pick_up = scanstop_datetime_object.time()
        pick_up_hour = pick_up.hour
        pick_up_minute = pick_up.minute
        if pick_up_minute == 0:
            pick_up_minute = "00"
        pickup_military  = str(pick_up_hour) + ':' + str(pick_up_minute)
        pickup_time = self.timeConvert(pickup_military)
        order_times = mridetails.OrderTimes(drop_off_time, pickup_time)
        return order_times

    def clean_part_name(self, name):
        # scrubbs the name object, removes ID and if M or F
        name_list = name.split('(')
        name = name_list[0]
        return name

    def clean_site_name(self, site):
        #corrects site, error check
        correct_site = site.lower()
        if "morton grove" in correct_site or "mg" in correct_site:
            scan_site = "Morton Grove"
            site_address = "9000 Waukegan Road, Morton Grove, IL"
        elif "u of c" in correct_site or "uc" in correct_site or "university of chicago" in correct_site:
            scan_site = "University of Chicago"
            site_address = "5812 S Ellis Ave, Chicago, IL"
        else:
            scan_site = "Scan site unknown: check to make sure site is correct in RADC system"
            site_address = "Scan site unknown: check to make sure site is correct in RADC system"
        site_info = mridetails.SiteDetails(scan_site, site_address)
        return site_info
