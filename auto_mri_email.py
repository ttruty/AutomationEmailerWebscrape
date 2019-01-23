#! Pythin 3.5
from tkinter import*
from tkinter import ttk
import mridefs as mri
import mriemailer as mriemail

class auto_mri_gui:
    def __init__(self, master):
        self.master = master
        self.master.geometry("400x375")
        self.master.wm_title("Auto MRI Email")
        self.step = 0

        self.frame1=Frame(master)
        self.frame2=Frame(master)
        self.frame3=Frame(master)
        self.frame1.pack()
        self.frame2.pack()
        self.frame3.pack()

        self.label1=Label(self.frame1, text="Staff List", font="Calibre 14")
        self.label1.grid(row=0, columnspan=2)
        self.label2=Label(self.frame1, text="Name:", font="Calibre 12")
        self.label2.grid(row=1, column=0)
        self.label3=Label(self.frame1, text="Staff ID:", font="Calibre 12")
        self.label3.grid(row=2, column=0)
        self.label4=Label(self.frame1, text="Staff Phone:", font="Calibre 12")
        self.label4.grid(row=3, column=0)

        self.name=StringVar()
        self.entry1=Entry(self.frame1,textvariable=self.name)
        self.entry1.grid(row=1, column=1)

        self.staff_id=StringVar()
        self.entry2=Entry(self.frame1,textvariable=self.staff_id)
        self.entry2.grid(row=2, column=1)

        self.staff_phone=StringVar()
        self.entry3=Entry(self.frame1,textvariable=self.staff_phone)
        self.entry3.grid(row=3, column=1)

        self.scrollbar=Scrollbar(self.frame2, orient=VERTICAL)

        self.listbox=Listbox(self.frame2, selectmode=EXTENDED, yscrollcommand=self.scrollbar.set,width=40) 
        self.listbox.grid(row=3, columnspan=3)

        self.scrollbar.config(command=self.listbox)

        self.button1=Button(self.frame2, text="Add", width=15, height=1, command=self.add)
        self.button1.grid(row=5, column=0)

        self.button2=Button(self.frame2, text="Delete",  width=15, height=1, command=self.delete)
        self.button2.grid(row=5, column=1)

        self.button3=Button(self.frame2, text="Save to file",  width=15, height=1, command=self.save)
        self.button3.grid(row=5, column=2)

        self.button4=Button(self.frame3, text="Generate Email", width=55, height=2, command=self.generate)
        self.master.bind('<Return>', lambda e: self.generate())
        self.button4.grid(row=8, column=0, columnspan=3, rowspan=2)

        self.progress = ttk.Progressbar(self.frame3, length=400)
        self.progress.grid(row=10, column=0, columnspan=3, rowspan=1, pady=(10, 10))

        self.staff_info = self.load()
        self.staff_ids = [item[1] for item in self.staff_info]
        
        
    def delete(self):
         select=self.listbox.curselection()
         index=select[0]
         self.listbox.delete(index)
         self.label1['text'] = "Staff List (Changed remember to save)"

    def add(self):
        name = self.entry1.get()
        staff_id = self.entry2.get()
        staff_phone = self.entry3.get()
    ##    name.set("")
    ##    staff_id.set("")
        self.listbox.insert(END, name + ':' + staff_id + ':' + staff_phone)
        if name=="":
            labelError=Label(self.frame1, text="Name is empty", fg="red")
            labelError.grid(columnspan=2)
        if staff_id=="":
            labelError2=Label(self.frame1, text="Staff ID is empty", fg="red")
            labelError2.grid(columnspan=2)
        if staff_phone=="":
            labelError3=Label(self.frame1, text="Staff phone is empty", fg="red")
            labelError3.grid(columnspan=2)
        self.entry1.delete(0, 'end')
        self.entry2.delete(0, 'end')
        self.entry3.delete(0, 'end')
        self.label1['text'] = "Staff List (Changed remember to save)"

    def save(self):
        list1=list(self.listbox.get(0,END))
        with open("staff.txt", "w") as myfile:
            for i in list1:
                myfile.write(str(i + ','))
        self.label1['text'] = "Staff List (Saved)"

    def load(self):
        staff_d = []
        with open('staff.txt','r') as f:
            lines =  f.read().split(',')
            for line in lines:
                if line != '':
                    self.listbox.insert(END, line)
                    staff_info = line.split(':')
                    staff_d.append(staff_info)
        return staff_d

    def reload(self):
        staff_d = []
        with open('staff.txt','r') as f:
            lines =  f.read().split(',')
            for line in lines:
                if line != '':
                    staff_info = line.split(':')
                    staff_d.append(staff_info)
        return staff_d        

    def generate(self):
        mri.mri_driver()
        mri.driver_open()
        
        self.staff_info = self.reload()
        self.staff_ids = [item[1] for item in self.staff_info]

        # task = mri.ThreadedTask(self.progress)
        # task.start()

        full_list, url_list, next_monday = mri.mri_driver.make_url(mri.mri_driver(), self.staff_ids)
        # self.progress.step(100)
        # self.progress.update()

        mri.driver_close()
        email_path = mriemail.setup_email(full_list, next_monday, self.staff_info)
        mriemail.create_email(email_path)

        #print(full_list, url_list, next_monday)

                    
    
mri.login_gui()
wn=Tk()
my_gui = auto_mri_gui(wn)
wn.mainloop()
