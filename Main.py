import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
from tkcalendar import DateEntry
from tkinter import PhotoImage
import pandas as pd



# Function to open the emp management interface------------------------------------------------------------------------------------------------------------------------------------------------

def open_emp_management():
    login_window.destroy()

#GUI INTERFACE-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Create or connect to the SQLite database
    conn = sqlite3.connect('Data/emp_info.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emp (
            Sr INTEGER PRIMARY KEY AUTOINCREMENT,
            "Full Name" VARCHAR(60) NOT NULL,
            "Employee ID" VARCHAR(6) UNIQUE NOT NULL,
            "Age" INTEGER NOT NULL,
            "Salary" FLOAT NOT NULL,
            "Date of Birth" DATE NOT NULL,
            "Department" VARCHAR(20) NOT NULL,
            "Contact No" INTEGER NOT NULL,
            "Address" VARCHAR(255) NOT NULL,
            "Gender" TEXT NOT NULL
        )
    ''')

    conn.commit()
    #FUNCTION-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    def export_data_to_excel():
        df = pd.read_sql_query("SELECT * FROM emp", conn)
        writer = pd.ExcelWriter('Data/EmployeeData.xlsx', engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Employee Data')
        writer.close()



    #ADD,UPDATE,DELETE,CLEAR FUNCTIONS

    def add_emp():
        full_name = full_name_entry.get()
        emp_id = emp_id_entry.get()
        age = age_entry.get()
        sal = sal_entry.get()
        dob = dob_entry.get()
        dept = dept_var.get()
        contact_no = contact_no_entry.get()
        
        # Remove newline characters and extra whitespace from the address
        address = address_entry.get("1.0", tk.END).strip().replace("\n", " ")
        
        gender = gender_var.get()

        # Check if all fields are filled
        if not (full_name and emp_id and age and sal and dob and dept and contact_no and address and gender):
            messagebox.showerror('Error', 'Please fill in all fields.')
            return

        # Check if Employee ID already exists in the database
        cursor.execute('SELECT 1 FROM emp WHERE "Employee ID" = ?', (emp_id,))
        if cursor.fetchone():
            messagebox.showerror('Duplicate ID', 'Employee ID already exists. Please enter a different ID.')
            return

        # Proceed with adding new employee data
        conn.execute('INSERT INTO emp ("Full Name", "Employee ID", "Age", "Salary", "Date of Birth", "Department", "Contact No", "Address", "Gender") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (full_name, emp_id, age, sal, dob, dept, contact_no, address, gender))
        conn.commit()
        clear_entries()
        update_emp_list()
        messagebox.showinfo('Success', 'Employee added successfully.')
        export_data_to_excel()




    def update_emp():
        selected_item = emp_tree.selection()
        if selected_item:
            original_emp_id = emp_tree.item(selected_item, 'values')[2]

            full_name = full_name_entry.get()
            emp_id = emp_id_entry.get()
            age = age_entry.get()
            sal = sal_entry.get()
            dob = dob_entry.get()
            dept = dept_var.get()
            contact_no = contact_no_entry.get()
            address = address_entry.get("1.0", tk.END).strip().replace("\n", " ")
            gender = gender_var.get()

            if full_name and emp_id and age and sal and dob and dept and contact_no and address and gender:
                # Check if the new Employee ID is already taken by another employee
                cursor.execute("SELECT `Employee ID` FROM emp WHERE `Employee ID`=? AND `Employee ID`!=?", (emp_id, original_emp_id))
                if cursor.fetchone():
                    messagebox.showerror("Error", "This Employee ID already exists. Please use a different ID.")
                else:
                    try:
                        conn.execute('UPDATE emp SET "Full Name"=?, "Employee ID"=?, "Age"=?, "Salary"=?, "Date of Birth"=?, "Department"=?, "Contact No"=?, "Address"=?, "Gender"=? WHERE "Employee ID"=?', (full_name, emp_id, age, sal, dob, dept, contact_no, address, gender, original_emp_id))
                        conn.commit()
                        clear_entries()
                        update_emp_list()
                        messagebox.showinfo("Success", "Employee information updated successfully.")
                    except Exception as e:
                        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            else:
                messagebox.showerror('Error', 'Please fill in all fields.')
        else:
            messagebox.showerror('Error', 'Please select an employee to update.')


    def delete_emp():
        selected_item = emp_tree.selection()
        if selected_item:
            emp_id = emp_tree.item(selected_item, 'values')[0]
            conn.execute('DELETE FROM emp WHERE Sr=?', (emp_id,))
            conn.execute('UPDATE emp SET Sr = Sr - 1 WHERE Sr > ?', (emp_id,))
            conn.commit()
            update_emp_list()
        else:
            messagebox.showerror('Error', 'Please select a student to delete.')

    def clear_all_emp():
        conn.execute('DELETE FROM emp')
        conn.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name = "emp"')
        conn.commit()
        update_emp_list()

    # function is used to clear the input fields after performing an operation like adding or updating a employee record.
    def clear_entries():
        full_name_entry.delete(0, tk.END)
        emp_id_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
        sal_entry.delete(0, tk.END)  
        dob_entry.set_date(None)  
        dept_var.set("") 
        contact_no_entry.delete(0, tk.END) 


    def select_record(event):
        selected_item = emp_tree.selection()
        if selected_item:
            values = emp_tree.item(selected_item, 'values')
            full_name_entry.delete(0, tk.END)
            full_name_entry.insert(0, values[1])
            
            # Disable validation temporarily while setting the employee ID
            emp_id_entry.configure(validate="none")
            emp_id_entry.delete(0, tk.END)
            emp_id_entry.insert(0, values[2])  
            emp_id_entry.configure(validate="key")


            age_entry.delete(0, tk.END)
            age_entry.insert(0, values[3])

            sal_entry.configure(validate="none")
            sal_entry.delete(0, tk.END)
            sal_entry.insert(0, values[4])
            sal_entry.configure(validate="key")

            dob_entry.set_date(values[5])
            dept_var.set(values[6])

            
            contact_no_entry.delete(0, tk.END)
            contact_no_entry.insert(0, values[7])
            


            address_entry.delete("1.0", tk.END)  
            address_entry.insert("1.0", values[8])  
            gender_var.set(values[9])  


    def retrieve_emp():
        cursor.execute('SELECT * FROM emp')
        emp = cursor.fetchall()
        return emp

    def update_emp_list():
        emps = retrieve_emp()
        emp_tree.delete(*emp_tree.get_children())
        for emp in emps:
            emp_tree.insert('', 'end', values=emp)

    #SEARCH AND CLEAR SEARCH FUNCTION

    def search_emp():
        search_criteria = search_entry.get().strip().lower()  
        if search_criteria:
            cursor.execute('''
                SELECT * FROM emp WHERE 
                lower("Full Name") LIKE ? OR
                lower("Employee ID") LIKE ? OR
                lower("Department") LIKE ? OR
                lower("Salary") LIKE ? OR
                lower("Contact No") LIKE ? OR
                lower("Age") LIKE ? OR
                (
                    lower("Gender") = 'male' AND ? = 'male' OR
                    lower("Gender") = 'female' AND ? = 'female'
                )
            ''',
            ('%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%', search_criteria, search_criteria))
            emps = cursor.fetchall()

            emp_tree.delete(*emp_tree.get_children())

            for emp in emps:
                emp_tree.insert('', 'end', values=emp)
        else:
            messagebox.showinfo('Info', 'Please enter a search criteria.')

    def clear_search():
        search_entry.delete(0, tk.END) 
        update_emp_list()

    def toggle_clear_button(event=None):
        if search_entry.get():
            clear_button.place(relx=0.98, rely=0.5, anchor="e")
        else:
            clear_button.place_forget()

    def limit_chars(*args):
        value = entry_text.get()
        if len(value) > 50:
            entry_text.set(value[:50])

    #VALIDATION-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def validate_age_input(P):
        if not P:
            return True 
        if P.isdigit():
            age = int(P)
            if 0 <= age <= 99:
                return True
        messagebox.showerror("Invalid Age", "Please enter a numeric value between 0 and 99 for Age.")
        return False

    def validate_sal_input(P):
        if not P:
            return True 
        if P.isdigit():
            sal = float(P)
            if 0 <= sal <= 5000000.000000:
                return True
        messagebox.showerror("Invalid Salary", "Please enter a numeric value between 0 and 50Lakh for Salary.")
        return False


    def validate_contact_input(P):
        # Validate while typing; allow incomplete (yet valid) number entry
        if len(P) == 0 or (P.isdigit() and len(P) <= 10):
            return True
        messagebox.showerror("Invalid Contact No", "Please enter up to 10 digits of numeric value for Contact No.")
        return False





    def validate_emp_id_input(P):
        if not P:
            return True
        if len(P) > 6:
            messagebox.showerror("Invalid Employee ID", "Please enter a maximum of 6 characters for Employee ID.")
            return False
        if len(P) == 6:  # Only check for duplicates when maximum length is reached
            entered_emp_id = P.lower()
            cursor.execute('SELECT "Employee ID" FROM emp')
            existing_ids = [row[0].lower() for row in cursor.fetchall()]

            if entered_emp_id in existing_ids:
                messagebox.showerror("Duplicate Employee ID", "Employee ID already exists. Please choose a different Employee ID.")
                return False
        return True




    def validate_full_name_input(P):
        if not P:
            return True  
        if len(P) <= 60:
            return True
        messagebox.showerror("Invalid Full Name", "Please enter a maximum of 60 characters for Full Name.")
        return False

    def validate_address_input(P):
        if not P:
            return True
        if len(P) <= 255:
            return True
        messagebox.showerror("Invalid Address", "Please enter a maximum of 255 characters for Address.")
        return False

    def validate_dept_input(P):
        if not P:
            return True 
        if len(P) <= 20:
            return True
        messagebox.showerror("Invalid Employee Department", "Please enter a maximum of 20 characters for Employee Department.")
        return False
   
    app = tk.Tk()
    app.title("Empower Hub")
    app.geometry("1920x1080")
    app.config(background="#E2EEFC")


    #SEARCH FRAME
    search_frame=tk.Frame(app,width=1883,height=66,bg="#092B53")
    search_frame.place(x=20, y=16)
    #HEAD NAME
    head_label=tk.Label(app,text="Empower Hub",font=("Inter",20,"bold"),bg="#092B53",fg="#FFFFFF")
    head_label.place(x=77,y=26)
    #SEARCH ENTRY 
    entry_text = tk.StringVar()
    entry_text.trace("w", limit_chars)
    search_entry=tk.Entry(app,bg="#FFFFFF",width=50,font=("Inter", 20,"bold"),fg="#092B53",textvariable=entry_text)
    search_entry.place(x=445,y=26,height=47)

    #SEARCH & CLEAR BUTTON FRAME
    button_frame = tk.Frame(search_entry,bg="#E2EEFC",width=100,height=50)
    button_frame.place(x=850,y=0)
    #CLEAR BUTTON
    clear_image = Image.open("Resources/clear.png")
    clear_image = clear_image.resize((45, 45))
    clear_image = ImageTk.PhotoImage(clear_image)
    clear_button = tk.Button(button_frame, image=clear_image, command=clear_search, bd=0, cursor="hand2", highlightthickness=0,background="#E2EEFC")
    clear_button.image = clear_image  # Store a reference to prevent garbage collection
    clear_button.place(x=10, y=0)
    # SHOW CLEAR BUTTON ONLY WHEN THE TEXT IS PRESENT IN SEARCH ENTRY
    search_entry.bind("<KeyRelease>", toggle_clear_button)
    toggle_clear_button()
    #SEARCH BUTTON
    search_image = Image.open("Resources/search.png")
    search_image = search_image.resize((45, 45))
    search_image = ImageTk.PhotoImage(search_image)
    search_button = tk.Button(button_frame, image=search_image, command=search_emp, bd=0, cursor="hand2", highlightthickness=3,background="#E2EEFC")
    search_button.image = search_image  # Store a reference to prevent garbage collection
    search_button.place(x=10, y=0)

    #ADD,UPDATE,DELETE,CLEAR ALL BUTTON FRAME
    button_frame_right = tk.Frame(search_frame,bg="#092B53",width=250) 
    button_frame_right.place(x=1500,y=10,height=47)
    #ADD BUTTON
    add_image = Image.open("Resources/add.png")
    add_image = add_image.resize((50, 50))
    add_image = ImageTk.PhotoImage(add_image)
    add_button = tk.Button(button_frame_right, image=add_image,command=add_emp, bd=0, cursor="hand2", highlightthickness=0,bg="#092B53")
    add_button.image = add_image  # Store a reference to prevent garbage collection
    add_button.place(x=5, y=1)
    # UPDATE BUTTON
    update_image = Image.open("Resources/update.png")
    update_image = update_image.resize((50, 45))
    update_image = ImageTk.PhotoImage(update_image)
    update_button = tk.Button(button_frame_right, image=update_image,command=update_emp, bd=0, cursor="hand2", highlightthickness=0,bg="#092B53")
    update_button.image = update_image  # Store a reference to prevent garbage collection
    update_button.place(x=50, y=1)
    #DELETE BUTTON
    delete_image = Image.open("Resources/delete.png")
    delete_image = delete_image.resize((45, 45))
    delete_image = ImageTk.PhotoImage(delete_image)
    delete_button = tk.Button(button_frame_right, image=delete_image,command=delete_emp, bd=0, cursor="hand2", highlightthickness=0,bg="#092B53")
    delete_button.image = delete_image  # Store a reference to prevent garbage collection
    delete_button.place(x=120, y=1)
    #CLEAR ALL BUTTON
    clear_all_image =Image.open("Resources/clearall.png")
    clear_all_image = clear_all_image.resize((45, 45))
    clear_all_image = ImageTk.PhotoImage(clear_all_image)
    clear_all_button = tk.Button(button_frame_right, image=clear_all_image,command=clear_all_emp, bd=0, cursor="hand2", highlightthickness=0,bg="#092B53")
    clear_all_button.image = clear_all_image  # Store a reference to prevent garbage collection
    clear_all_button.place(x=180, y=1)

    #FORM FRMAE
    form_frame=tk.Frame(app,bg="#E2EEFC",width=1883,height=300)
    form_frame.place(x=20,y=100)


    #Validation
    validate_full_name = form_frame.register(validate_full_name_input)
    validate_emp_id = form_frame.register(validate_emp_id_input)
    validate_age = form_frame.register(validate_age_input)
    validate_sal = form_frame.register(validate_sal_input)
    validate_dept = form_frame.register(validate_dept_input)
    validate_contact = form_frame.register(validate_contact_input)
    validate_address = form_frame.register(validate_address_input)


    #FORM DETAILS
    full_name_label = tk.Label(form_frame, text="Full Name:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    full_name_entry = tk.Entry(form_frame,validate="key", validatecommand=(validate_full_name, "%P"), width=60, font=("Inter", 15,"bold"),relief="solid",bd=1)
    emp_id_label = tk.Label(form_frame, text="Employee ID:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    emp_id_entry = tk.Entry(form_frame, validate="key", validatecommand=(validate_emp_id, "%P"), width=10, font=("Inter", 15,"bold"),relief="solid",bd=1)
    age_label = tk.Label(form_frame, text="Age:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    age_entry = tk.Entry(form_frame,validate="key", validatecommand=(validate_age, "%P"), width=10, font=("Inter", 15,"bold"),relief="solid",bd=1)
    sal_label = tk.Label(form_frame, text="Salary:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    sal_entry = tk.Entry(form_frame,validate="key", validatecommand=(validate_sal, "%P") ,width=14, font=("Inter", 15,"bold"),relief="solid",bd=1)
    dob_label = tk.Label(form_frame, text="DOB:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    dob_entry = DateEntry(form_frame, date_pattern="dd-mm-yyyy", width=10, font=("Inter", 15,"bold"),relief="solid",bd=1)
    dept_label = tk.Label(form_frame, text="Department:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    dept_var = tk.StringVar()
    dept_var.set("Other")
    dept_dropdown = ttk.Combobox(form_frame, textvariable=dept_var, values=["Accounts", "Engineer","Developer"], width=8,font=("Inter", 15,"bold"))
    contact_no_label = tk.Label(form_frame, text="Contact No:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    contact_no_entry = tk.Entry(form_frame,validate="key", validatecommand=(validate_contact, "%P"), width=10, font=("Inter", 15,"bold"),relief="solid",bd=1)
    address_label = tk.Label(form_frame, text="Address:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    address_entry = tk.Text(form_frame, height=5, width=60,font=("Inter", 15,"bold"),relief="solid",bd=1)
    address_entry.bind("<KeyRelease>", lambda event, text_widget=address_entry: validate_address_input(text_widget.get("1.0", "end-1c")))
    gender_label = tk.Label(form_frame, text="Gender:", font=("Inter", 15,"bold"),bg="#E2EEFC",fg="#092B53")
    gender_var = tk.StringVar()
    gender_var.set("Male")
    male_radio = tk.Radiobutton(form_frame, text="Male", variable=gender_var, value="Male",font=("Inter", 15,"bold"),relief="flat",bd=1,bg="#E2EEFC",fg="#092B53")
    female_radio = tk.Radiobutton(form_frame, text="Female", variable=gender_var, value="Female",font=("Inter", 15,"bold"),relief="flat",bd=1,bg="#E2EEFC",fg="#092B53")




    #PLACING A DETAILS
    full_name_label.place(x=10, y=10)
    full_name_entry.place(x=120, y=10)
    emp_id_label.place(x=1000, y=10)
    emp_id_entry.place(x=1135, y=10)
    age_label.place(x=1325,y=10)
    age_entry.place(x=1425,y=10)
    sal_label.place(x=1600,y=10)
    sal_entry.place(x=1680,y=10)
    dob_label.place(x=10,y=80)
    dob_entry.place(x=450,y=80)
    dept_label.place(x=1000, y=80)
    dept_dropdown.place(x=1135,y=80)
    contact_no_label.place(x=1300,y=80)
    contact_no_entry.place(x=1425,y=80)
    address_label.place(x=10,y=160)
    address_entry.place(x=120,y=160)
    gender_label.place(x=1000,y=160)
    male_radio.place(x=1135,y=160)
    female_radio.place(x=1325,y=160)





  

    #RESULT FRAME
    result_frame=tk.Frame(app,width=1883,height=610,bg="#FFFFFF",bd=1,relief="solid")
    result_frame.place(x=20,y=428)
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Inter", 15, "bold"))  # Set column header font and style
    style.configure("Treeview", font=("Inter", 15))  # Set cell font and style
    #HEADING 
    emp_tree = ttk.Treeview(result_frame, columns=("Sr", "Full Name", "Employee ID", "Age", "Salary", "DOB", "Department", "Contact No", "Address", "Gender"), show="headings")
    emp_tree.heading("Sr", text="Sr No")
    emp_tree.heading("Full Name", text="Full Name")
    emp_tree.heading("Employee ID", text="Employee ID")
    emp_tree.heading("Age", text="Age")
    emp_tree.heading("Salary", text="Salary")
    emp_tree.heading("DOB", text="DOB")
    emp_tree.heading("Department", text="Department")
    emp_tree.heading("Contact No", text="Contact No")
    emp_tree.heading("Address", text="Address")
    emp_tree.heading("Gender", text="Gender")
    emp_tree.place(x=1,y=1)
    #COLUMN
    emp_tree["height"] =29
    emp_tree.column("Sr", width=30)
    emp_tree.column("Full Name", width=300)
    emp_tree.column("Employee ID", width=150)
    emp_tree.column("Age", width=50)
    emp_tree.column("Salary", width=100)
    emp_tree.column("DOB", width=100)
    emp_tree.column("Department", width=150)
    emp_tree.column("Contact No", width=150)
    emp_tree.column("Address", width=766)
    emp_tree.column("Gender", width=80)


    update_emp_list()
    emp_tree.bind("<ButtonRelease-1>", select_record)
    app.mainloop()
    conn.close()
        
    app.mainloop()


#Function to handle login------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def login():
    entered_username = username_entry.get()
    entered_password = password_entry.get()
    if entered_username == 'admin' and entered_password == '123':
        open_emp_management()
    else:
        messagebox.showerror("Login Error", "Invalid username or password")

# Function to toggle password visibility
def toggle_password_visibility():
    if password_entry.cget('show') == '•':
        password_entry.config(show='')
        eye_icon_button.config(image=eye_open_icon)
    else:
        password_entry.config(show='•')
        eye_icon_button.config(image=eye_closed_icon)


    

# GUI OF LOGIN WINDOW ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("1920x1080")  # Set the window size to fullscreen

bg_image = Image.open("Resources/bg.jpg")
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(login_window, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

frame_width = 450
frame_height = 300
frame_x = (login_window.winfo_screenwidth() - frame_width) // 2  # Center horizontally
frame_y = (login_window.winfo_screenheight() - frame_height) // 2  # Center vertically

frame = tk.Canvas(login_window, bg="white", highlightthickness=0)
frame.place(x=frame_x, y=frame_y, width=frame_width, height=frame_height)

login_label = ttk.Label(frame, text="SIGN UP", foreground="dark orange", background="white", font=("Trebuchet MS", 20,"bold"))
login_label.place(relx=0.1, rely=0.05, anchor="nw") 

username_label = ttk.Label(frame, text="Username", foreground="black", background="white", font=("Trebuchet MS", 12))
username_label.place(relx=0.1, rely=0.3, anchor="w")

username_entry = ttk.Entry(frame, font=("Helvetica", 12), width=39)
username_entry.place(relx=0.1, rely=0.4, anchor="w")

password_label = ttk.Label(frame, text="Password", foreground="black", background="white", font=("Trebuchet MS", 12))
password_label.place(relx=0.1, rely=0.5, anchor="w")

password_entry = ttk.Entry(frame, show='•', font=("Helvetica", 12), width=39)  
password_entry.place(relx=0.1, rely=0.6, anchor="w")

eye_open_image = Image.open("Resources/view.png")
eye_open_image = eye_open_image.resize((18, 18), Image.LANCZOS) 
eye_open_icon = ImageTk.PhotoImage(eye_open_image)

eye_closed_image = Image.open("Resources/hide.png")
eye_closed_image = eye_closed_image.resize((18, 18), Image.LANCZOS) 
eye_closed_icon = ImageTk.PhotoImage(eye_closed_image)

eye_icon_button = tk.Button(password_entry, image=eye_closed_icon, command=toggle_password_visibility, bd=0, bg="white", cursor="hand2")
eye_icon_button.place(relx=1, rely=0.5, anchor="e")

login_button = tk.Button(frame, text="LOGIN", command=login, width=44, height=2, background="dark orange",foreground="white",font=("Trebuchet MS", 10,"bold"),borderwidth=0,highlightthickness=0, cursor="hand2")
login_button.place(relx=0.1, rely=0.85, anchor="w") 

login_window.mainloop()



