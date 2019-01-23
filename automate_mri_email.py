import datetime, time, mridetails, io, os, collections, getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()

list_link = []
logged_in = False
staff_ids = ['847', '854']

now = datetime.datetime.now()
#now = datetime.datetime(2016, 10, 4, 18, 00) # this is used to test different weeks
next_week_url_list = []
mri_dict = {}
scan_dict = {}

def login_gui():
    username = input('username: ')
    password = getpass.getpass()
    return username, password

def login():
    # logs into webpage
    global logged_in
    
    # will only run once when called in program, once runned logged_in == True
    while logged_in == False:
        # Select the Username and Password
        us, pw = login_gui()
        username = driver.find_elements_by_xpath('//*[@id="j_username"]')[0]
        username.send_keys('ttruty')
        password = driver.find_elements_by_xpath('//*[@id="j_password"]')[0]
        password.send_keys('pk97nw')
        # Submit the form
        login_button = driver.find_element_by_xpath('//*[@id="submit"]')
        login_button.click()
        logged_in = True

def part_info(part_url):
        # this pulls the name, address, phone number from the participant summary page
        driver.get(part_url)
        web_elem_name = driver.find_elements_by_xpath('//*[@id="header_table"]/tbody/tr[1]/td[1]')
        part_name = web_elem_name[0].text
        part_name = clean_part_name(part_name)
        web_elem_address = driver.find_elements_by_xpath('//*[@id="overview"]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr[3]/td')
        part_address = web_elem_address[0].text
        web_elem_phone = driver.find_elements_by_xpath('//*[@id="overview"]/div/div[1]/div[1]/div[2]/table[1]/tbody/tr[4]/td')
        part_phone = web_elem_phone[0].text
        part_info = mridetails.ParticipantDetails(part_name, part_address, part_phone)
        return part_info

def get_scan_info(url):
    # this pulls the scan info from the daily schedule page
    global list_link
    part_links = []
    scan_time = []
    scan_name = []
    scan_obj = []
    part_obj = []
    new_part_obj = []
    scans_this_day = 0
    appts_this_day = 0
    comp_list =[]

    # driver behind opening pages and getting data
    driver.get(url)
    time.sleep(1) # thsi seems to fix the problem of overrunning webpages
    login() # this should only run once

    appt_details = driver.find_elements_by_xpath("/html/body/div[3]/table/tbody/tr[2]/td[9]")

    #time and day of scans
    all_scans_date_time = driver.find_elements_by_xpath("/html/body/div[3]/table/tbody/tr/td[5]")
    # participant name
    all_scans_name = driver.find_elements_by_xpath("/html/body/div[3]/table/tbody/tr/td[3]")
    # which site the scan will be at
    site_info = driver.find_elements_by_xpath("/html/body/div[3]/table/tbody/tr[2]/td[6]")

    # this cleans the scan time
    for span in all_scans_date_time:
        seporated_times = (span.text).splitlines()
        true_time_scan = seporated_times[0]
        scan_time.append(true_time_scan)
        appts_this_day = appts_this_day + 1
        
    # this cleans the particpant name data
    for span in all_scans_name:
        seporated_name = (span.text).splitlines()
        true_name_scan = seporated_name[0]
        scan_name.append(true_name_scan)

    # scan site info    
    for span in site_info:
        scan_site = span.text

    for span in appt_details:
        appt = appt_details[0].text
    
    
    i = 0 # indexes each scan in day
    index = 1
    
    while i < appts_this_day: # as long as the index is below the number of scan it will run
        if "Neuro-Imaging" in appt:
            scan_time_obj = scan_time[i]
            #print(scan_time[i]) # i is the index of the current scanning participant 
            #print(scan_name[i*2]) # name xpath is iterated over, X2 because of elements in xpath (I THINK IT IS NOTES)
            scan_site_obj = scan_site
            #print(scan_site)    # Site
            scan_info = mridetails.ScanDetails(scan_time_obj, scan_site_obj, appt)
            #print("scan number   " + str(i))
            scan_obj.append(scan_info)
            # this finds the links for the particpant summary page
            id_links = driver.find_element_by_xpath("/html/body/div[3]/table/tbody/tr[" + str(index * 2) + "]/td[2]/a")
            #print(id_links.text)
            part_page = (id_links.get_attribute('href'))
            part_links.append(part_page)
            i = i + 1
            index = index + 1
            scans_this_day = scans_this_day + 1
        else:
            break
    for url in part_links:
        part_obj.append(part_info(url)) # creates list of all the scans that day
    
    new_part_obj = check_same_addr(part_obj)
    #print(new_part_obj)
    return scan_obj, new_part_obj

def check_same_addr(object_list):
    # checks to see if the address is the object list input is repeated
    combine_name = []
    new_part_list = []
    isduplicate = False
    if len(object_list) > 1:
        for i in object_list:
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
            
                  
def next_weekday(d, weekday):
    # returns next week day
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def make_url():
    # returns a list of all the urls for staff daily schedule of next week
    global next_week_url_list
    global mri_dict
    global next_monday
    d = datetime.date(now.year, now.month, now.day)
    next_monday = next_weekday(d, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    #print('Next Monday is:    ' + str(next_monday))
    

    # format next monday to be used in RADC WEBPAGE
    next_monday_year = str(next_monday)[:4]
    next_monday_month = str(next_monday)[5:7]
    next_monday_day = str(next_monday)[8:10]

    # url for staff MONDAY schedule of NEXT week
    for ids in staff_ids:
        baseURL = 'https://radc.rush.edu/radc/schedule/staffDailySchedule.htm?style=1'
        staffURL = baseURL + '&month=' + next_monday_month + '&year=' + next_monday_year + '&day=' + next_monday_day + '&intid=' + ids

    # look at each webpage for each DAY OF THE WEEK FOR CURRENT STAFF/WEEK
        for i in range(5):
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
            # Prints URL for all days in week
            weekday = (next_weekday(d, i))
            next_week_url = baseURL + '&month=' + next_monday_month + '&year=' + next_monday_year + '&day=' + str(next_day) + '&intid=' + ids
            #print(next_week_url)
            #get_scan_info(next_week_url)
            next_week_url_list.append(next_week_url)
    for url in next_week_url_list:
        mri_dict[url] = get_scan_info(url)     
    return next_week_url_list

def order_time(time):
    ''' time is in this format : Thu 10/13/2016 3:00 PM - 4:15 PM '''   
    time_list = time.split()
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
    drop_off_time = str(drop_off_hour) + ':' + str(drop_off_minute)

    pick_up = scanstop_datetime_object.time()
    pick_up_hour = pick_up.hour
    pick_up_minute = pick_up.minute
    if pick_up_minute == 0:
        pick_up_minute = "00"
    pickup_time  = str(pick_up_hour) + ':' + str(pick_up_minute)
    order_times = mridetails.OrderTimes(drop_off_time, pickup_time)
    return order_times

def order_time_2(time1, time2):
    ''' ONLY USED WHEN 2 SCANS'''
    ''' time is in this format : Thu 10/13/2016 3:00 PM - 4:15 PM '''   
    time1_list = time1.split()
    time2_list = time2.split()
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

    #
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
    drop_off_time = str(drop_off_hour) + ':' + str(drop_off_minute)

    pick_up = scanstop_datetime_object.time()
    pick_up_hour = pick_up.hour
    pick_up_minute = pick_up.minute
    if pick_up_minute == 0:
        pick_up_minute = "00"
    pickup_time  = str(pick_up_hour) + ':' + str(pick_up_minute)
    order_times = mridetails.OrderTimes(drop_off_time, pickup_time)
    return order_times

def staff_details(staff_id):
    # gives the staff details of who is the scanning investigator
    if staff_id == "847":
        staff_name = "Tim"
        staff_phone = "630-615-8684"
    elif staff_id == "854":
        staff_name = "Dominique"
        staff_phone = "517-749-0291"
    else:
        staff_name = "UNKNOWN"
        staff_phone = "UNKNOWN"
    staff_info = mridetails.StaffDetails(staff_id, staff_name, staff_phone)
    return staff_info


def clean_part_name(name):
    # scrubbs the name object, removes ID and if M or F
    name_list = name.split('(')
    name = name_list[0]
    return name

def clean_site_name(site):
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

#this is the main running of program
make_url()
driver.quit()


# FIRST DELETES THE FILE THEN OPEN THE NEW FILE FOR WRITING
#os.remove("next_weeks_orders" + str(next_monday) + ".txt")
filename = "next_weeks_orders" + str(next_monday) + ".txt"
folder = "scan_orders"
if not os.path.exists(folder):
    os.makedirs(folder)
with open(os.path.join(folder, filename), 'w') as myfile:
    myfile.write("Orders for the week of: " + str(next_monday))
    myfile.write("\n")
    myfile.write("\n")


# this pulls only the days with scans
    for k,v in mri_dict.items():
            if v != ([], ([], False)):
                scan_dict[k] = v

    #this prints daily stuffs for each scan day
    ## TODO: SORT DICT, KEY IS weekday number from MAKE URL
    for k,v in scan_dict.items():
            
        for i in range(len(v[1][0])):
            staff_id = (k[-3:])
            staff = staff_details(staff_id)
            scan_details = v[0]
            combine_travel = v[1][1]
            participant_object = v[1][0]
            #print(k, "scan: " + v[0][i].time, v[0][i].site, v[0][i].appt, "participant " + v[1][i].name, v[1][i].address, v[1][i].phone)
            clean_name = clean_part_name(v[1][0][i].name)
            clean_site = clean_site_name(v[0][i].site)
            time_list = v[0][i].time.split()
            drop_date = time_list[0] + " " + time_list[1]

            if combine_travel == True:
                order = order_time_2(v[0][0].time, v[0][-1].time)
            else:
                order = order_time(v[0][i].time)
                

##            print(staff.id)
##            print(staff.name)
##            print(staff.phone)
##                       
##            print("drop off date: " + drop_date)
##            print("Drop off time: " + order.dropoff)
##            print("Pick up time: " + order.pickup)
##            print(v[0][i].time)
##            print(clean_name)
##            print(v[1][i].address)
##            print(v[1][i].phone)
##            print(clean_site.name)
##            print(clean_site.address)

            # THIS WRITE INFO TO FILE
            myfile.write("Scan date: " + drop_date)
            myfile.write('\n')
            myfile.write(staff.name + " " + staff.phone + " will be the contact at the site: ")
            myfile.write('\n')
            myfile.write(clean_site.name)
            myfile.write('\n')
            myfile.write("Drop off time: " + order.dropoff)
            myfile.write('\n')
            myfile.write("Pick up time: " + order.pickup)
            myfile.write('\n')
            myfile.write("Participant name: " + clean_name)
            myfile.write('\n')
            myfile.write("Participant address: " + v[1][0][i].address)
            myfile.write('\n')
            myfile.write("Participant Phone: " + v[1][0][i].phone)
            myfile.write('\n')
            myfile.write("Mri Site to drop off: " + clean_site.name + " " + clean_site.address)
            myfile.write('\n')
            myfile.write('\n')
            myfile.write('\n')

#COUPLES TRAVELLING TOGETHER
	    
# WHAT SCAN DOCUMENT SHOULD LOOK LIKE
'''
PLEASE NOTE: DRIVER SHOULD CALL PARTICIPANTS 15 MINUTES BEFORE ARRIVAL. DRIVER SHOULD CALL ON-SITE CONTACT FIVE MINUTES BEFORE ARRIVAL AND WAIT WITH PARTICIPANT UNTIL CONTACT MEETS THE CAR
 
[DAY/DATE]: [STAFF.name (STAFF.phone] will be the contact at the site: [SITE.site]
 
[SCAN.i]                [PART.name], [PART.address], tel: [PART.phone]
To arrive at the [SITE.site] scan site [SITE.address] at [SCAN DROP OFF TIME], pick-up at [SCAN FINISH THIME]

REPEAT FOR SCANS EACH DAY... MOVE TO NEXT DAY
 '''
