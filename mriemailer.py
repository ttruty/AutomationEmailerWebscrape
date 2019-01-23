import mridefs as mri
import mridetails
import os
import win32com.client as win32

def setup_email(full_list, next_monday, staff_list):
    m = mri.mri_driver()

    header = '''
    <b>PLEASE NOTE: DRIVER SHOULD CALL PARTICIPANTS <i>15 MINUTES</i> BEFORE ARRIVAL.
    DRIVER SHOULD CALL ON-SITE CONTACT FIVE MINUTES BEFORE ARRIVAL AND WAIT
    WITH PARTICIPANT UNTIL CONTACT MEETS THEM.</b><br><br>
    '''

    # FIRST DELETES THE FILE THEN OPEN THE NEW FILE FOR WRITING
    #os.remove("next_weeks_orders" + str(next_monday) + ".txt")
    filename = "next_weeks_orders" + str(next_monday) + ".txt"
    folder = "scan_orders"
    if not os.path.exists(folder):
        os.makedirs(folder)
    full_path = os.path.join(folder, filename)
    
    #staff_info = mridetails.StaffDetails(staff_id, staff_name, staff_phone)
    
    
    with open(full_path, 'w') as myfile:
        myfile.write("<b>Orders for the week of: " + str(next_monday) + '</b>' + '<br><br>')
        myfile.write(header)

        full_list = [x for x in full_list if x != ([], ([], False))]
        mri_full_list = sorted(full_list, key=lambda x: int(x[0][0].time.split()[2].split('/')[1])) # sorts the list according to dates
        for day in mri_full_list:
            try:
                #print(day[0][0].time)
                #print(len(day[1][0]))
                for i in range(len(day[1][0])):
                    print(day[0][i])
                    scan_deets = day[0][i]
                    combine_travel = day[1][1]
                    staff_id = day[0][i].staff
                    items = [x for x in staff_list if staff_id == x[1]]
                    staff = mridetails.StaffDetails(items[0][1], items[0][0], items[0][2])
                    clean_site = m.clean_site_name(scan_deets.site)
                    time_list = scan_deets.time.split()
                    drop_date = time_list[1] + " " + time_list[2]

                    if combine_travel:
                        clean_name = m.clean_part_name(day[1][0][i-1].name)
                        order = m.order_time_2(day[0][0].time, day[0][-1].time)
                        part_deets = day[1][0][i-1]
                    else:
                        order = m.order_time(scan_deets.time)
                        clean_name = m.clean_part_name(day[1][0][i].name)
                        part_deets = day[1][0][i]

    #******************THIS WRITE INFO TO FILE****************************************
                    # try:
                    #     gotdata = dlist[1]
                    # except IndexError:
                    #     gotdata = 'null'

                    myfile.write("Scan date: " + "<b>" + drop_date + "</b><br>")
                    myfile.write('\n')
                    myfile.write("<b>" + staff.name + " " + "(" + staff.phone + ")" + " will be the contact at the site: </b>")
                    myfile.write('<br>\n')
                    myfile.write("<b>" + clean_site.name + "</b>")
                    myfile.write('<br>\n')
                    myfile.write("Drop off time: " + order.dropoff)
                    myfile.write('<br>\n')
                    myfile.write("Pick up time: " + order.pickup)
                    myfile.write('<br>\n')
                    myfile.write("Participant name: " + clean_name)
                    myfile.write('<br>\n')
                    myfile.write("Participant address: " + part_deets.address)
                    myfile.write('<br>\n')
                    myfile.write("Participant Phone: " + part_deets.phone)
                    myfile.write('<br>\n')
                    myfile.write("MRI Site to drop off/pickup: " + "<b>" + clean_site.name + '</b>' + " " + clean_site.address)
                    myfile.write('<br>\n')
                    myfile.write('<br>\n')
                    myfile.write('<br>\n')
            except IndexError:
                myfile.write("Scan date: " + "<b>" + "ERROR MANUALLY ENTER DATA" + "</b><br>")
                myfile.write('\n')
                myfile.write(
                    "<b>" + staff.name + " " + "(" + staff.phone + ")" + " will be the contact at the site: </b>")
                myfile.write('<br>\n')
                myfile.write("<b>" + "ERROR MANUALLY ENTER DATA" + "</b>")
                myfile.write('<br>\n')
                myfile.write("Drop off time: " + "ERROR MANUALLY ENTER DATA")
                myfile.write('<br>\n')
                myfile.write("Pick up time: " + "ERROR MANUALLY ENTER DATA")
                myfile.write('<br>\n')
                myfile.write("Participant name: " + "ERROR MANUALLY ENTER DATA")
                myfile.write('<br>\n')
                myfile.write("Participant address: " + "ERROR MANUALLY ENTER DATA")
                myfile.write('<br>\n')
                myfile.write("Participant Phone: " + "ERROR MANUALLY ENTER DATA")
                myfile.write('<br>\n')
                myfile.write(
                    "MRI Site to drop off/pickup: " + "<b>" + "ERROR MANUALLY ENTER DATA" + '</b>' + " " + "ERROR MANUALLY ENTER DATA")
                myfile.write('<br>\n')
                myfile.write('<br>\n')
                myfile.write('<br>\n')

    return full_path
# ************** CREATING EMAIL ************************

def Emailer(text, subject, recipient, auto=False):   

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = subject
    mail.HtmlBody = text
    if auto:
        mail.send
    else:
        mail.Display(True) # or whatever the correct code is

def create_email(path):
    with open(path, 'r') as myfile:      
        text = myfile.read()
        Emailer(text, "Next Week's Orders", 'mail@chicagolimousine.com', False)
