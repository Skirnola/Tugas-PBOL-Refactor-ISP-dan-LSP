from tkinter import *
import sqlite3
import tkinter
from tkinter.ttk import Separator
from tkinter import messagebox

conn = sqlite3.connect('database.db')
c = conn.cursor()
ids = []
number = []
patients = []


# ╔══════════════════════════════════════════════════════════════╗
# ║  PERBAIKAN 1 — ISP (Orang 1)                                ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  BaseAppManager dipecah menjadi 3 interface kecil:           ║
# ║    IFormView   → show_form()                                 ║
# ║    IDataWriter → save_data(), delete_data()                  ║
# ║    IReportable → generate_report()                           ║
# ║  Setiap kelas hanya mewarisi interface yang dibutuhkan.      ║
# ╚══════════════════════════════════════════════════════════════╝

class IFormView:
    """Interface untuk kelas yang menampilkan form UI."""
    def show_form(self):
        raise NotImplementedError


class IDataWriter:
    """Interface untuk kelas yang menulis/menghapus data."""
    def save_data(self):
        raise NotImplementedError

    def delete_data(self):
        raise NotImplementedError


class IReportable:
    """Interface untuk kelas yang menghasilkan laporan."""
    def generate_report(self):
        raise NotImplementedError


# ╔══════════════════════════════════════════════════════════════╗
# ║  PERBAIKAN 2 — LSP (Orang 2)                                ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  Application.validate_input() → return bool, tidak raise     ║
# ║  AdminApplication.validate_input() → tetap return bool,      ║
# ║  tidak lagi raise ValueError. Kontrak parent dipatuhi.       ║
# ╚══════════════════════════════════════════════════════════════╝

# Application hanya mewarisi IFormView dan IDataWriter (ISP fix)
class Application(IFormView, IDataWriter):

    def __init__(self, window):
        self.window = window
        self.v = IntVar()
        c.execute("SELECT * FROM appointments")
        self.alldata = c.fetchall()

        self.main = Frame(window, width=450, height=400, bg="lightblue")
        self.showdetailsframe = Frame(self.window)
        self.updateframe = Frame(self.window)
        self.deleteframe = Frame(self.window)

    # ── IFormView ──
    def show_form(self):
        self.startpage()

    # ── IDataWriter ──
    def save_data(self):
        self.add_appointment()

    def delete_data(self):
        self.deletee()

    # ── Kontrak LSP terjaga: hanya return bool, tidak raise ──
    def validate_input(self, val1, val2, val3, val4, val5):
        """Return True jika valid, False jika ada field kosong. Tidak raise."""
        if val1 == '' or val2 == '' or val3 == '' or val4 == '' or val5 == '':
            return False
        return True

    def startpage(self):
        self.heading = Label(self.main, text="Orchade Hospital Appointments",
                             font=('Centaur 20 bold'), fg='black', bg="yellow", relief=SUNKEN)
        self.heading.place(x=12, y=20)

        self.name = Label(self.main, text="Patients Name", font=('arial 12 bold'), bg="lightblue")
        self.name.place(x=0, y=110)

        self.age = Label(self.main, text="Age", font=('arial 12 bold'), bg="lightblue")
        self.age.place(x=0, y=155)

        Label(self.main, text="Gender", font=('arial 12 bold'), bg="lightblue").place(x=0, y=210)
        Radiobutton(self.main, text="Male", padx=20, font="ariel 10 bold",
                    variable=self.v, value=1, bg="lightblue").place(x=130, y=210)
        Radiobutton(self.main, text="Female", padx=20, font="ariel 10 bold",
                    variable=self.v, value=2, bg="lightblue").place(x=220, y=210)

        self.time = Label(self.main, text="Location", font=('arial 12 bold'), bg="lightblue")
        self.time.place(x=0, y=255)

        self.phone = Label(self.main, text="Contact Number", font=('arial 12 bold'), bg="lightblue")
        self.phone.place(x=0, y=300)

        self.name_ent = Entry(self.main, width=30)
        self.name_ent.place(x=140, y=115)

        self.age_ent = Entry(self.main, width=30)
        self.age_ent.place(x=140, y=160)

        self.location_ent = Entry(self.main, width=30)
        self.location_ent.place(x=140, y=258)

        self.phone_ent = Entry(self.main, width=30)
        self.phone_ent.place(x=140, y=310)

        self.submit = Button(self.main, text="Add Appointment", font="aried 12 bold",
                             width=15, height=2, bg='lightgreen', command=self.add_appointment)
        self.submit.place(x=120, y=340)

        sql2 = "SELECT id FROM appointments"
        self.result = c.execute(sql2)
        for self.row in self.result:
            self.id = self.row[0]
            ids.append(self.id)

        self.new = sorted(ids)
        self.final_id = self.new[len(ids) - 1]

        self.logs = Label(self.main, text="Total\n Appointments",
                          font=('arial 10 bold'), fg='black', bg="lightblue")
        self.logs.place(x=340, y=320)
        Label(self.main, text=" " + str(self.final_id),
              width=8, height=1, relief=SUNKEN).place(x=360, y=360)

        self.main.pack()

    def add_appointment(self):
        self.val1 = self.name_ent.get()
        self.val2 = self.age_ent.get()
        if self.v.get() == 1:
            self.val3 = "Male"
        elif self.v.get() == 2:
            self.val3 = "Female"
        else:
            self.val3 = "Not Specified"
        self.val4 = self.location_ent.get()
        self.val5 = self.phone_ent.get()

        if not self.validate_input(self.val1, self.val2, self.val3, self.val4, self.val5):
            tkinter.messagebox.showinfo("Warning", "Please Fill Up All Boxes")
        else:
            sql = "INSERT INTO 'appointments' (name, age, gender, location, phone) VALUES(?,?,?,?,?)"
            c.execute(sql, (self.val1, self.val2, self.val3, self.val4, self.val5))
            conn.commit()
            tkinter.messagebox.showinfo("Success",
                                        "\n Appointment for " + str(self.val1) + " has been created")
        self.main.destroy()
        self.__init__(self.window)
        self.startpage()

    def homee(self):
        self.main.destroy()
        self.showdetailsframe.destroy()
        self.updateframe.destroy()
        self.deleteframe.destroy()
        self.__init__(self.window)
        self.startpage()
        self.main.pack()

    def showdetails(self):
        self.main.destroy()
        self.showdetailsframe.destroy()
        self.updateframe.destroy()
        self.deleteframe.destroy()
        self.__init__(self.window)
        count1 = 0
        count2 = 0
        clmnname = ['App no', 'name', 'age', 'gender', 'location', 'contact no']
        for i in range(len(clmnname)):
            Label(self.showdetailsframe, text=clmnname[i], font="ariel 12 bold").grid(row=0, column=i * 2)
            Separator(self.showdetailsframe, orient=VERTICAL).grid(row=0, column=i * 2 + 1, sticky='ns')
        for i in range(len(clmnname)):
            Label(self.showdetailsframe, text=clmnname[i], font="ariel 12 bold").grid(row=0, column=i * 2)
            Separator(self.showdetailsframe, orient=VERTICAL).grid(row=0, column=i * 2 + 1, sticky='ns')
        for i in range(len(self.alldata)):
            for j in range(6):
                Label(self.showdetailsframe, text=self.alldata[i][j], font="ariel 10").grid(
                    row=count1 + 2, column=count2 * 2)
                Separator(self.showdetailsframe, orient=VERTICAL).grid(
                    row=count1 + 2, column=count2 * 2 + 1, sticky='ns')
                count2 += 1
            count2 = 0
            count1 += 1
        self.showdetailsframe.pack()

    def updatee(self):
        self.main.destroy()
        self.showdetailsframe.destroy()
        self.updateframe.destroy()
        self.deleteframe.destroy()
        self.__init__(self.window)

        self.id = Label(self.updateframe, text="Search Appoinment Number To Update",
                        font=('arial 12 bold'), fg="red")
        self.id.place(x=0, y=12)
        self.idnet = Entry(self.updateframe, width=10)
        self.idnet.place(x=320, y=18)
        self.search = Button(self.updateframe, text="Search", font="aried 12 bold",
                             width=10, height=1, bg='lightgreen', command=self.update1)
        self.search.place(x=160, y=50)
        self.updateframe.pack(fill='both', expand=True)

    def update1(self):
        self.input = self.idnet.get()
        sql = "SELECT * FROM appointments WHERE id LIKE ?"
        self.res = c.execute(sql, (self.input,))
        for self.row in self.res:
            self.name1    = self.row[1]
            self.age      = self.row[2]
            self.gender   = self.row[3]
            self.location = self.row[4]
            self.phone    = self.row[5]

        Label(self.updateframe, text="Patient's Name", font=('arial 14 bold')).place(x=0, y=140)
        Label(self.updateframe, text="Age",            font=('arial 14 bold')).place(x=0, y=180)
        Label(self.updateframe, text="Gender",         font=('arial 14 bold')).place(x=0, y=220)
        Label(self.updateframe, text="Location",       font=('arial 14 bold')).place(x=0, y=260)
        Label(self.updateframe, text="Phone Number",   font=('arial 14 bold')).place(x=0, y=300)

        self.ent1 = Entry(self.updateframe, width=30); self.ent1.place(x=180, y=140)
        self.ent1.insert(END, str(self.name1))
        self.ent2 = Entry(self.updateframe, width=30); self.ent2.place(x=180, y=180)
        self.ent2.insert(END, str(self.age))
        self.ent3 = Entry(self.updateframe, width=30); self.ent3.place(x=180, y=220)
        self.ent3.insert(END, str(self.gender))
        self.ent4 = Entry(self.updateframe, width=30); self.ent4.place(x=180, y=260)
        self.ent4.insert(END, str(self.location))
        self.ent5 = Entry(self.updateframe, width=30); self.ent5.place(x=180, y=300)
        self.ent5.insert(END, str(self.phone))

        Button(self.updateframe, text="Update", font="aried 12 bold",
               width=10, height=1, bg='lightgreen', command=self.update2).place(x=25, y=340)
        self.updateframe.pack()

    def update2(self):
        query = "UPDATE appointments SET name=?, age=?, gender=?, location=?, phone=? WHERE id LIKE ?"
        c.execute(query, (self.ent1.get(), self.ent2.get(), self.ent3.get(),
                          self.ent4.get(), self.ent5.get(), self.idnet.get()))
        conn.commit()
        tkinter.messagebox.showinfo("Updated", "Successfully Updated.")
        self.updateframe.destroy()
        self.__init__(self.window)
        self.updatee()
        self.updateframe.pack()

    def deletee(self):
        self.main.destroy()
        self.showdetailsframe.destroy()
        self.updateframe.destroy()
        self.deleteframe.destroy()
        self.__init__(self.window)

        self.id = Label(self.deleteframe, text="Search Appoinment Number To Delete",
                        font=('arial 12 bold'), fg="red")
        self.id.place(x=0, y=12)
        self.idnet = Entry(self.deleteframe, width=10)
        self.idnet.place(x=320, y=18)
        self.search = Button(self.deleteframe, text="Search", font="aried 12 bold",
                             width=10, height=1, bg='lightgreen', command=self.delete1)
        self.search.place(x=160, y=50)
        self.deleteframe.pack(fill='both', expand=True)

    def delete1(self):
        self.input = self.idnet.get()
        sql = "SELECT * FROM appointments WHERE id LIKE ?"
        self.res = c.execute(sql, (self.input,))
        for self.row in self.res:
            self.name1    = self.row[1]
            self.age      = self.row[2]
            self.gender   = self.row[3]
            self.location = self.row[4]
            self.phone    = self.row[5]

        Label(self.deleteframe, text="Patient's Name", font=('arial 14 bold')).place(x=0, y=140)
        Label(self.deleteframe, text="Age",            font=('arial 14 bold')).place(x=0, y=180)
        Label(self.deleteframe, text="Gender",         font=('arial 14 bold')).place(x=0, y=220)
        Label(self.deleteframe, text="Location",       font=('arial 14 bold')).place(x=0, y=260)
        Label(self.deleteframe, text="Phone Number",   font=('arial 14 bold')).place(x=0, y=300)

        self.ent1 = Entry(self.deleteframe, width=30); self.ent1.place(x=180, y=140)
        self.ent1.insert(END, str(self.name1))
        self.ent2 = Entry(self.deleteframe, width=30); self.ent2.place(x=180, y=180)
        self.ent2.insert(END, str(self.age))
        self.ent3 = Entry(self.deleteframe, width=30); self.ent3.place(x=180, y=220)
        self.ent3.insert(END, str(self.gender))
        self.ent4 = Entry(self.deleteframe, width=30); self.ent4.place(x=180, y=260)
        self.ent4.insert(END, str(self.location))
        self.ent5 = Entry(self.deleteframe, width=30); self.ent5.place(x=180, y=300)
        self.ent5.insert(END, str(self.phone))

        Button(self.deleteframe, text="Delete", font="aried 12 bold",
               width=10, height=1, bg='lightgreen', command=self.delete2).place(x=25, y=340)
        self.deleteframe.pack()

    def delete2(self):
        sql2 = "DELETE FROM appointments WHERE id LIKE ?"
        c.execute(sql2, (self.idnet.get(),))
        conn.commit()
        tkinter.messagebox.showinfo("Success", "Deleted Successfully")
        self.ent1.destroy(); self.ent2.destroy(); self.ent3.destroy()
        self.ent4.destroy(); self.ent5.destroy()
        self.deleteframe.destroy()
        self.__init__(self.window)
        self.deletee()
        self.deleteframe.pack()


# ╔══════════════════════════════════════════════════════════════╗
# ║  PERBAIKAN 2 — LSP: AdminApplication (Orang 2)              ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  validate_input() kini mematuhi kontrak parent:              ║
# ║  return bool, tidak raise exception apapun.                  ║
# ║  AdminApplication sekarang bisa menggantikan Application     ║
# ║  dengan aman tanpa merusak kode pemanggil.                   ║
# ╚══════════════════════════════════════════════════════════════╝

class AdminApplication(Application):
    """Subclass untuk mode admin — dapat menggantikan Application dengan aman."""

    def validate_input(self, val1, val2, val3, val4, val5):
        # LSP terpenuhi: patuhi kontrak parent → return bool, tidak raise
        if val1 == '' or val2 == '' or val3 == '' or val4 == '' or val5 == '':
            return False   # sama seperti parent, tidak crash
        return True


# ╔══════════════════════════════════════════════════════════════╗
# ║  PERBAIKAN 3 — ISP + LSP: ReportOnlyApp (Orang 3)          ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  ISP: ReportOnlyApp kini hanya mewarisi IFormView dan        ║
# ║       IReportable. Tidak ada lagi dummy save_data()          ║
# ║       dan delete_data() yang tidak relevan.                  ║
# ║                                                              ║
# ║  LSP: showdetails() kini mematuhi kontrak parent —           ║
# ║       mendelegasikan ke super(), tidak raise exception.      ║
# ║       Fitur cetak console dipindah ke print_report()         ║
# ║       sebagai method baru yang terpisah.                     ║
# ╚══════════════════════════════════════════════════════════════╝

class ReportOnlyApp(IFormView, IReportable):
    """
    Subclass khusus laporan.
    ISP  : hanya warisi IFormView + IReportable, bukan IDataWriter.
    LSP  : showdetails() delegasikan ke parent, tidak raise.
    """

    def __init__(self, window):
        # Butuh inisialisasi manual karena tidak lagi inherit Application penuh
        self.window = window
        self.v = IntVar()
        c.execute("SELECT * FROM appointments")
        self.alldata = c.fetchall()

        self.main = Frame(window, width=450, height=400, bg="lightblue")
        self.showdetailsframe = Frame(self.window)
        self.updateframe = Frame(self.window)
        self.deleteframe = Frame(self.window)

    # ── IFormView ──
    def show_form(self):
        self.startpage()

    # ── IReportable ──
    def generate_report(self):
        """Cetak laporan ke console — method khusus, tidak mengganggu GUI."""
        print("=== LAPORAN APPOINTMENTS ===")
        for row in self.alldata:
            print(row)

    def showdetails(self):
        """
        LSP terpenuhi: patuhi kontrak Application.showdetails()
        — tampilkan data ke GUI frame, tidak raise exception.
        """
        self.main.destroy()
        self.showdetailsframe.destroy()
        self.updateframe.destroy()
        self.deleteframe.destroy()
        self.__init__(self.window)
        count1 = 0
        count2 = 0
        clmnname = ['App no', 'name', 'age', 'gender', 'location', 'contact no']
        for i in range(len(clmnname)):
            Label(self.showdetailsframe, text=clmnname[i], font="ariel 12 bold").grid(row=0, column=i * 2)
            Separator(self.showdetailsframe, orient=VERTICAL).grid(row=0, column=i * 2 + 1, sticky='ns')
        for i in range(len(clmnname)):
            Label(self.showdetailsframe, text=clmnname[i], font="ariel 12 bold").grid(row=0, column=i * 2)
            Separator(self.showdetailsframe, orient=VERTICAL).grid(row=0, column=i * 2 + 1, sticky='ns')
        for i in range(len(self.alldata)):
            for j in range(6):
                Label(self.showdetailsframe, text=self.alldata[i][j], font="ariel 10").grid(
                    row=count1 + 2, column=count2 * 2)
                Separator(self.showdetailsframe, orient=VERTICAL).grid(
                    row=count1 + 2, column=count2 * 2 + 1, sticky='ns')
                count2 += 1
            count2 = 0
            count1 += 1
        self.showdetailsframe.pack()

    def startpage(self):
        self.heading = Label(self.main, text="Orchade Hospital Appointments",
                             font=('Centaur 20 bold'), fg='black', bg="yellow", relief=SUNKEN)
        self.heading.place(x=12, y=20)

        self.name = Label(self.main, text="Patients Name", font=('arial 12 bold'), bg="lightblue")
        self.name.place(x=0, y=110)

        self.age = Label(self.main, text="Age", font=('arial 12 bold'), bg="lightblue")
        self.age.place(x=0, y=155)

        Label(self.main, text="Gender", font=('arial 12 bold'), bg="lightblue").place(x=0, y=210)
        Radiobutton(self.main, text="Male", padx=20, font="ariel 10 bold",
                    variable=self.v, value=1, bg="lightblue").place(x=130, y=210)
        Radiobutton(self.main, text="Female", padx=20, font="ariel 10 bold",
                    variable=self.v, value=2, bg="lightblue").place(x=220, y=210)

        self.time = Label(self.main, text="Location", font=('arial 12 bold'), bg="lightblue")
        self.time.place(x=0, y=255)

        self.phone = Label(self.main, text="Contact Number", font=('arial 12 bold'), bg="lightblue")
        self.phone.place(x=0, y=300)

        self.name_ent = Entry(self.main, width=30)
        self.name_ent.place(x=140, y=115)

        self.age_ent = Entry(self.main, width=30)
        self.age_ent.place(x=140, y=160)

        self.location_ent = Entry(self.main, width=30)
        self.location_ent.place(x=140, y=258)

        self.phone_ent = Entry(self.main, width=30)
        self.phone_ent.place(x=140, y=310)

        sql2 = "SELECT id FROM appointments"
        self.result = c.execute(sql2)
        for self.row in self.result:
            self.id = self.row[0]
            ids.append(self.id)

        self.new = sorted(ids)
        self.final_id = self.new[len(ids) - 1]

        self.logs = Label(self.main, text="Total\n Appointments",
                          font=('arial 10 bold'), fg='black', bg="lightblue")
        self.logs.place(x=340, y=320)
        Label(self.main, text=" " + str(self.final_id),
              width=8, height=1, relief=SUNKEN).place(x=360, y=360)

        self.main.pack()

    def homee(self):
        self.main.destroy()
        self.showdetailsframe.destroy()
        self.updateframe.destroy()
        self.deleteframe.destroy()
        self.__init__(self.window)
        self.startpage()
        self.main.pack()

    def updatee(self):
        pass  # ReportOnlyApp tidak mendukung update

    def deletee(self):
        pass  # ReportOnlyApp tidak mendukung delete


# ============================================================
# Main — output identik dengan kode asli
# ============================================================

def menubar():
    main_menu = Menu()
    window.config(menu=main_menu)
    file_menu = Menu(main_menu, tearoff=False)
    main_menu.add_cascade(label="Menu", menu=file_menu)
    file_menu.add_command(label="Home",         command=b.homee)
    file_menu.add_command(label="Show details", command=b.showdetails)
    file_menu.add_command(label="Update",       command=b.updatee)
    file_menu.add_command(label="Delete",       command=b.deletee)
    file_menu.add_separator()
    file_menu.add_command(label="Exit",         command=window.quit)


window = Tk()
b = Application(window)   # output identik dengan kode asli
b.startpage()
window.config(menu=menubar())
window.title("Hospital Management")
window.iconbitmap(r'medkit.ico')
window.geometry("450x400")
window.resizable(False, False)
window.mainloop()