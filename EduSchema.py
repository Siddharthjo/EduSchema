import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import logging

# Configure logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

# Establish database connection
try:
    # Establishing a connection to the MySQL database
    db_connection = mysql.connector.connect(
        host="localhost",    # Hostname where MySQL server is running
        port=3306,           # Port number MySQL server is listening on
        user="root",         # MySQL username
        password="Root@5566",  # MySQL password
        database="EduSchema" # Name of the database you created
    )

    # Creating a cursor object to interact with the database
    cursor = db_connection.cursor()

except mysql.connector.Error as err:
    # Handle database connection errors
    messagebox.showerror("Database Connection Error", f"Error: {err}")
    exit(1)

# Functions for Course Management
def fetch_courses(search_query="", order_by="course_id", order_dir="ASC"):
    try:
        query = "SELECT * FROM Courses WHERE is_deleted = FALSE"
        if search_query:
            query += " AND (course_name LIKE %s OR course_description LIKE %s)"
            query += f" ORDER BY {order_by} {order_dir}"
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        else:
            query += f" ORDER BY {order_by} {order_dir}"
            cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        logging.error(f"Error fetching courses: {e}")
        messagebox.showerror("Error", f"Error fetching courses: {e}")
        return []

def add_course():
    course_name = course_name_entry.get()
    course_description = course_description_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    if course_name and start_date and end_date:
        try:
            cursor.execute("INSERT INTO Courses (course_name, course_description, start_date, end_date) VALUES (%s, %s, %s, %s)", 
                           (course_name, course_description, start_date, end_date))
            db_connection.commit()
            refresh_courses()
            clear_course_entries()
        except mysql.connector.Error as e:
            logging.error(f"Error adding course: {e}")
            messagebox.showerror("Error", f"Error adding course: {e}")
    else:
        messagebox.showwarning("Input Error", "Please fill all mandatory fields")

def update_course():
    selected_course = course_list.focus()
    if selected_course:
        course_id = course_list.item(selected_course)['values'][0]
        course_name = course_name_entry.get()
        course_description = course_description_entry.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        if course_name and start_date and end_date:
            try:
                cursor.execute("UPDATE Courses SET course_name=%s, course_description=%s, start_date=%s, end_date=%s WHERE course_id=%s",
                               (course_name, course_description, start_date, end_date, course_id))
                db_connection.commit()
                refresh_courses()
                clear_course_entries()
            except mysql.connector.Error as e:
                logging.error(f"Error updating course: {e}")
                messagebox.showerror("Error", f"Error updating course: {e}")
        else:
            messagebox.showwarning("Input Error", "Please fill all mandatory fields")
    else:
        messagebox.showwarning("Selection Error", "Please select a course to update")

def clear_course_entries():
    course_name_entry.delete(0, tk.END)
    course_description_entry.delete(0, tk.END)
    start_date_entry.delete(0, tk.END)
    end_date_entry.delete(0, tk.END)

def delete_course():
    selected_course = course_list.focus()
    if selected_course:
        course_id = course_list.item(selected_course)['values'][0]
        try:
            cursor.execute("UPDATE Courses SET is_deleted = TRUE WHERE course_id = %s", (course_id,))
            db_connection.commit()
            refresh_courses()
        except mysql.connector.Error as e:
            logging.error(f"Error deleting course: {e}")
            messagebox.showerror("Error", f"Error deleting course: {e}")
    else:
        messagebox.showwarning("Selection Error", "Please select a course to delete")

def refresh_courses(search_query="", order_by="course_id", order_dir="ASC"):
    course_list.delete(*course_list.get_children())
    for course in fetch_courses(search_query, order_by, order_dir):
        course_list.insert("", tk.END, values=course)

def show_deleted_courses():
    try:
        cursor.execute("SELECT * FROM Courses WHERE is_deleted = TRUE")
        deleted_courses = cursor.fetchall()
        if deleted_courses:
            messagebox.showinfo("Deleted Courses", f"Deleted Courses: {deleted_courses}")
        else:
            messagebox.showinfo("Deleted Courses", "No courses have been deleted.")
    except mysql.connector.Error as e:
        logging.error(f"Error fetching deleted courses: {e}")
        messagebox.showerror("Error", f"Error fetching deleted courses: {e}")

def search_courses():
    search_query = course_search_entry.get()
    refresh_courses(search_query)

#Initialize global variables for sorting
current_sort_column = "course_id"
current_sort_direction = "ASC"

# Sorting function
def sort_courses(column, order_dir):
    global current_sort_column, current_sort_direction
    current_sort_column = column
    current_sort_direction = order_dir
    order_dir = "ASC" if order_dir == "DESC" else "DESC"
    refresh_courses(order_by=column, order_dir=order_dir)
    update_column_headers()

def update_column_headers():
    for col in course_columns:
        col_text = f"{col}"
        if col == current_sort_column:
            if current_sort_direction == "ASC":
                col_text += " ▲"
            else:
                col_text += " ▼"
        course_list.heading(col, text=col_text, command=lambda _col=col: sort_courses(_col, "ASC"))

# Sorting function for button
def sort_courses_by_button():
    selected_sort_option = sort_option.get()
    if selected_sort_option:
        column, order_dir = selected_sort_option.split()
        sort_courses(column, order_dir)

# Functions for Student Management
def fetch_students():
    try:
        cursor.execute("SELECT * FROM Students WHERE is_deleted = FALSE")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching students: {e}")
        return []

def add_student():
    first_name = student_first_name_entry.get()
    last_name = student_last_name_entry.get()
    email = student_email_entry.get()
    phone = student_phone_entry.get()
    if first_name and last_name and email:
        try:
            cursor.execute("INSERT INTO Students (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s)",
                           (first_name, last_name, email, phone))
            db_connection.commit()
            refresh_students()
            clear_student_entries()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error adding student: {e}")
    else:
        messagebox.showwarning("Input Error", "Please fill all mandatory fields")

def clear_student_entries():
    student_first_name_entry.delete(0, tk.END)
    student_last_name_entry.delete(0, tk.END)
    student_email_entry.delete(0, tk.END)
    student_phone_entry.delete(0, tk.END)

def delete_student():
    selected_student = student_list.focus()
    if selected_student:
        student_id = student_list.item(selected_student)['values'][0]
        try:
            cursor.execute("UPDATE Students SET is_deleted = TRUE WHERE student_id = %s", (student_id,))
            db_connection.commit()
            refresh_students()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error deleting student: {e}")
    else:
        messagebox.showwarning("Selection Error", "Please select a student to delete")

def refresh_students():
    student_list.delete(*student_list.get_children())
    for student in fetch_students():
        student_list.insert("", tk.END, values=student)

def show_deleted_students():
    try:
        cursor.execute("SELECT * FROM Students WHERE is_deleted = TRUE")
        deleted_students = cursor.fetchall()
        if deleted_students:
            messagebox.showinfo("Deleted Students", f"Deleted Students: {deleted_students}")
        else:
            messagebox.showinfo("Deleted Students", "No students have been deleted.")
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching deleted students: {e}")

# Functions for Assessment Management
def fetch_assessments():
    try:
        cursor.execute("SELECT * FROM Assessments WHERE is_deleted = FALSE")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching assessments: {e}")
        return []

def add_assessment():
    course_id = assessment_course_id_entry.get()
    assessment_name = assessment_name_entry.get()
    due_date = assessment_due_date_entry.get()
    if course_id and assessment_name and due_date:
        try:
            cursor.execute("INSERT INTO Assessments (course_id, assessment_name, due_date) VALUES (%s, %s, %s)", 
                           (course_id, assessment_name, due_date))
            db_connection.commit()
            refresh_assessments()
            clear_assessment_entries()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error adding assessment: {e}")
    else:
        messagebox.showwarning("Input Error", "Please fill all mandatory fields")

def clear_assessment_entries():
    assessment_course_id_entry.delete(0, tk.END)
    assessment_name_entry.delete(0, tk.END)
    assessment_due_date_entry.delete(0, tk.END)

def delete_assessment():
    selected_assessment = assessment_list.focus()
    if selected_assessment:
        assessment_id = assessment_list.item(selected_assessment)['values'][0]
        try:
            cursor.execute("UPDATE Assessments SET is_deleted = TRUE WHERE assessment_id = %s", (assessment_id,))
            db_connection.commit()
            refresh_assessments()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error deleting assessment: {e}")
    else:
        messagebox.showwarning("Selection Error", "Please select an assessment to delete")

def refresh_assessments():
    assessment_list.delete(*assessment_list.get_children())
    for assessment in fetch_assessments():
        assessment_list.insert("", tk.END, values=assessment)

def show_deleted_assessments():
    try:
        cursor.execute("SELECT * FROM Assessments WHERE is_deleted = TRUE")
        deleted_assessments = cursor.fetchall()
        if deleted_assessments:
            messagebox.showinfo("Deleted Assessments", f"Deleted Assessments: {deleted_assessments}")
        else:
            messagebox.showinfo("Deleted Assessments", "No assessments have been deleted.")
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching deleted assessments: {e}")

# Functions for Enrollment Management
def fetch_enrollments():
    try:
        cursor.execute("SELECT * FROM Enrollments WHERE is_deleted = FALSE")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching enrollments: {e}")
        return []

def add_enrollment():
    student_id = enrollment_student_id_entry.get()
    course_id = enrollment_course_id_entry.get()
    enrollment_date = enrollment_date_entry.get()
    if student_id and course_id and enrollment_date:
        try:
            cursor.execute("INSERT INTO Enrollments (student_id, course_id, enrollment_date) VALUES (%s, %s, %s)", 
                           (student_id, course_id, enrollment_date))
            db_connection.commit()
            refresh_enrollments()
            clear_enrollment_entries()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error adding enrollment: {e}")
    else:
        messagebox.showwarning("Input Error", "Please fill all mandatory fields")

def clear_enrollment_entries():
    enrollment_student_id_entry.delete(0, tk.END)
    enrollment_course_id_entry.delete(0, tk.END)
    enrollment_date_entry.delete(0, tk.END)

def delete_enrollment():
    selected_enrollment = enrollment_list.focus()
    if selected_enrollment:
        enrollment_id = enrollment_list.item(selected_enrollment)['values'][0]
        try:
            cursor.execute("UPDATE Enrollments SET is_deleted = TRUE WHERE enrollment_id = %s", (enrollment_id,))
            db_connection.commit()
            refresh_enrollments()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error deleting enrollment: {e}")
    else:
        messagebox.showwarning("Selection Error", "Please select an enrollment to delete")

def refresh_enrollments():
    enrollment_list.delete(*enrollment_list.get_children())
    for enrollment in fetch_enrollments():
        enrollment_list.insert("", tk.END, values=enrollment)

def show_deleted_enrollments():
    try:
        cursor.execute("SELECT * FROM Enrollments WHERE is_deleted = TRUE")
        deleted_enrollments = cursor.fetchall()
        if deleted_enrollments:
            messagebox.showinfo("Deleted Enrollments", f"Deleted Enrollments: {deleted_enrollments}")
        else:
            messagebox.showinfo("Deleted Enrollments", "No enrollments have been deleted.")
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching deleted enrollments: {e}")

# Functions for Grade Management
def fetch_grades():
    try:
        cursor.execute("SELECT * FROM Grades WHERE is_deleted = FALSE")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching grades: {e}")
        return []

def add_grade():
    enrollment_id = grade_enrollment_id_entry.get()
    assessment_id = grade_assessment_id_entry.get()
    grade = grade_value_entry.get()
    if enrollment_id and assessment_id and grade:
        try:
            cursor.execute("INSERT INTO Grades (enrollment_id, assessment_id, grade) VALUES (%s, %s, %s)", 
                           (enrollment_id, assessment_id, grade))
            db_connection.commit()
            refresh_grades()
            clear_grade_entries()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error adding grade: {e}")
    else:
        messagebox.showwarning("Input Error", "Please fill all mandatory fields")

def clear_grade_entries():
    grade_enrollment_id_entry.delete(0, tk.END)
    grade_assessment_id_entry.delete(0, tk.END)
    grade_value_entry.delete(0, tk.END)

def delete_grade():
    selected_grade = grade_list.focus()
    if selected_grade:
        grade_id = grade_list.item(selected_grade)['values'][0]
        try:
            cursor.execute("UPDATE Grades SET is_deleted = TRUE WHERE grade_id = %s", (grade_id,))
            db_connection.commit()
            refresh_grades()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error deleting grade: {e}")
    else:
        messagebox.showwarning("Selection Error", "Please select a grade to delete")

def refresh_grades():
    grade_list.delete(*grade_list.get_children())
    for grade in fetch_grades():
        grade_list.insert("", tk.END, values=grade)

def show_deleted_grades():
    try:
        cursor.execute("SELECT * FROM Grades WHERE is_deleted = TRUE")
        deleted_grades = cursor.fetchall()
        if deleted_grades:
            messagebox.showinfo("Deleted Grades", f"Deleted Grades: {deleted_grades}")
        else:
            messagebox.showinfo("Deleted Grades", "No grades have been deleted.")
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching deleted grades: {e}")

# Functions for Instructor Management
def fetch_instructors():
    try:
        cursor.execute("SELECT * FROM Instructors WHERE is_deleted = FALSE")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching instructors: {e}")
        return []

def add_instructor():
    first_name = instructor_first_name_entry.get()
    last_name = instructor_last_name_entry.get()
    email = instructor_email_entry.get()
    phone = instructor_phone_entry.get()
    if first_name and last_name and email:
        try:
            cursor.execute("INSERT INTO Instructors (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s)",
                           (first_name, last_name, email, phone))
            db_connection.commit()
            refresh_instructors()
            clear_instructor_entries()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error adding instructor: {e}")
    else:
        messagebox.showwarning("Input Error", "Please fill all mandatory fields")

def clear_instructor_entries():
    instructor_first_name_entry.delete(0, tk.END)
    instructor_last_name_entry.delete(0, tk.END)
    instructor_email_entry.delete(0, tk.END)
    instructor_phone_entry.delete(0, tk.END)

def delete_instructor():
    selected_instructor = instructor_list.focus()
    if selected_instructor:
        instructor_id = instructor_list.item(selected_instructor)['values'][0]
        try:
            cursor.execute("UPDATE Instructors SET is_deleted = TRUE WHERE instructor_id = %s", (instructor_id,))
            db_connection.commit()
            refresh_instructors()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error deleting instructor: {e}")
    else:
        messagebox.showwarning("Selection Error", "Please select an instructor to delete")

def refresh_instructors():
    instructor_list.delete(*instructor_list.get_children())
    for instructor in fetch_instructors():
        instructor_list.insert("", tk.END, values=instructor)

def show_deleted_instructors():
    try:
        cursor.execute("SELECT * FROM Instructors WHERE is_deleted = TRUE")
        deleted_instructors = cursor.fetchall()
        if deleted_instructors:
            messagebox.showinfo("Deleted Instructors", f"Deleted Instructors: {deleted_instructors}")
        else:
            messagebox.showinfo("Deleted Instructors", "No instructors have been deleted.")
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Error fetching deleted instructors: {e}")

# Initialize GUI
root = tk.Tk()
root.title("EduSchema")
root.geometry("1000x800")  # Set initial window size

def set_dark_styles():
    style = ttk.Style()
    style.configure("TButton",
                    padding=6,
                    relief="flat",
                    background="#3F51B5",  # Example: Blue background
                    foreground="#FFFFFF",  # Example: White text
                    font=('Helvetica', 10, 'bold'))  # Example: Bold font
    style.map("TButton",
              background=[("active", "#303F9F")])  # Example: Darker blue on hover

    style.configure("TEntry",
                    padding=5,
                    relief="solid",
                    font=('Helvetica', 10),
                    background="#424242",  # Example: Dark gray background
                    foreground="#FFFFFF")  # Example: White text

    style.configure("Treeview",
                    background="#424242",  # Example: Dark gray background
                    foreground="#FFFFFF",  # Example: White text
                    rowheight=25,
                    fieldbackground="#424242")  # Example: Dark gray row background

    style.configure("Treeview.Heading",
                    font=('Helvetica', 10, 'bold'),
                    background="#333333")  # Example: Darker gray header background

    style.map("Treeview",
              background=[("selected", "#3F51B5")])  # Example: Blue background for selected rows

set_dark_styles()  # Apply dark theme styles


notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky='nsew')

# Course Management Tab
course_tab = ttk.Frame(notebook)
notebook.add(course_tab, text='Courses')

course_tab.columnconfigure(1, weight=1)

# Course Form Frame
course_form_frame = ttk.Frame(course_tab, padding="10 10 10 10")
course_form_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
course_form_frame.columnconfigure(1, weight=1)

ttk.Label(course_form_frame, text="Course Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
course_name_entry = ttk.Entry(course_form_frame)
course_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(course_form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
course_description_entry = ttk.Entry(course_form_frame)
course_description_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(course_form_frame, text="Start Date:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
start_date_entry = ttk.Entry(course_form_frame)
start_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(course_form_frame, text="End Date:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
end_date_entry = ttk.Entry(course_form_frame)
end_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

ttk.Button(course_form_frame, text="Add Course", command=add_course).grid(row=4, columnspan=2, pady=10)
ttk.Button(course_form_frame, text="Update Course", command=update_course).grid(row=5, columnspan=2, pady=10)

# Course Search Frame
course_search_frame = ttk.Frame(course_tab, padding="10 10 10 10")
course_search_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
course_search_frame.columnconfigure(1, weight=1)

ttk.Label(course_search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
course_search_entry = ttk.Entry(course_search_frame)
course_search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
ttk.Button(course_search_frame, text="Search", command=search_courses).grid(row=0, column=2, padx=5, pady=5)

# Course List Frame
course_list_frame = ttk.Frame(course_tab)
course_list_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
course_list_frame.columnconfigure(0, weight=1)
course_list_frame.rowconfigure(0, weight=1)

# Course List Treeview
course_columns = ('course_id', 'course_name', 'course_description', 'start_date', 'end_date')
course_list = ttk.Treeview(course_list_frame, columns=course_columns, show='headings')

for col in course_columns:
    course_list.heading(col, text=col, command=lambda _col=col: sort_courses(_col, "ASC"))

course_list.grid(row=0, column=0, sticky='nsew')

course_scroll = ttk.Scrollbar(course_list_frame, orient="vertical", command=course_list.yview)
course_list.configure(yscrollcommand=course_scroll.set)
course_scroll.grid(row=0, column=1, sticky='ns')

refresh_courses()  # Initial load of courses

# Add Delete and Show Deleted Courses Buttons
ttk.Button(course_tab, text="Delete Course", command=delete_course).grid(row=3, column=0, pady=5)
ttk.Button(course_tab, text="Show Deleted Courses", command=show_deleted_courses).grid(row=4, column=0, pady=5)

# Sorting Options Frame
sort_options_frame = ttk.Frame(course_tab, padding="10 10 10 10")
sort_options_frame.grid(row=5, column=0, padx=10, pady=10, sticky='ew')
sort_options_frame.columnconfigure(1, weight=1)

sort_option = tk.StringVar()
sort_option.set("")  # Default empty option

ttk.Label(sort_options_frame, text="Sort by:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
sort_combobox = ttk.Combobox(sort_options_frame, textvariable=sort_option, values=[
    "course_id ASC", "course_id DESC",
    "course_name ASC", "course_name DESC",
    "start_date ASC", "start_date DESC",
    "end_date ASC", "end_date DESC"
])
sort_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Button(sort_options_frame, text="Sort", command=sort_courses_by_button).grid(row=0, column=2, padx=5, pady=5)

# Student Management Tab
student_tab = ttk.Frame(notebook)
notebook.add(student_tab, text='Students')

student_tab.columnconfigure(1, weight=1)

# Student Form Frame
student_form_frame = ttk.Frame(student_tab, padding="10 10 10 10")
student_form_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
student_form_frame.columnconfigure(1, weight=1)

ttk.Label(student_form_frame, text="First Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
student_first_name_entry = ttk.Entry(student_form_frame)
student_first_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(student_form_frame, text="Last Name:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
student_last_name_entry = ttk.Entry(student_form_frame)
student_last_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(student_form_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
student_email_entry = ttk.Entry(student_form_frame)
student_email_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(student_form_frame, text="Phone:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
student_phone_entry = ttk.Entry(student_form_frame)
student_phone_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

ttk.Button(student_form_frame, text="Add Student", command=add_student).grid(row=4, columnspan=2, pady=10)

# Student List Frame
student_list_frame = ttk.Frame(student_tab, padding="10 10 10 10")
student_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

student_list_frame.rowconfigure(0, weight=1)
student_list_frame.columnconfigure(0, weight=1)

# Student List Treeview
student_list = ttk.Treeview(student_list_frame, columns=("ID", "First Name", "Last Name", "Email", "Phone"), show='headings')
student_list.heading("ID", text="ID")
student_list.heading("First Name", text="First Name")
student_list.heading("Last Name", text="Last Name")
student_list.heading("Email", text="Email")
student_list.heading("Phone", text="Phone")
# student_list.heading("Deleted", text="Deleted")
student_list.grid(row=0, column=0, sticky='nsew')

student_scrollbar = ttk.Scrollbar(student_list_frame, orient=tk.VERTICAL, command=student_list.yview)
student_list.configure(yscroll=student_scrollbar.set)
student_scrollbar.grid(row=0, column=1, sticky='ns')

# Delete Student Button
ttk.Button(student_tab, text="Delete Selected Student", command=delete_student).grid(row=2, column=0, pady=10)

# Show Deleted Students Button
ttk.Button(student_tab, text="Show Deleted Students", command=show_deleted_students).grid(row=3, column=0, pady=10)

# Assessment Management Tab
assessment_tab = ttk.Frame(notebook)
notebook.add(assessment_tab, text='Assessments')

assessment_tab.columnconfigure(1, weight=1)

# Assessment Form Frame
assessment_form_frame = ttk.Frame(assessment_tab, padding="10 10 10 10")
assessment_form_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
assessment_form_frame.columnconfigure(1, weight=1)

ttk.Label(assessment_form_frame, text="Course ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
assessment_course_id_entry = ttk.Entry(assessment_form_frame)
assessment_course_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(assessment_form_frame, text="Assessment Name:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
assessment_name_entry = ttk.Entry(assessment_form_frame)
assessment_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(assessment_form_frame, text="Due Date:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
assessment_due_date_entry = ttk.Entry(assessment_form_frame)
assessment_due_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

ttk.Button(assessment_form_frame, text="Add Assessment", command=add_assessment).grid(row=3, columnspan=2, pady=10)

# Assessment List Frame
assessment_list_frame = ttk.Frame(assessment_tab, padding="10 10 10 10")
assessment_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

assessment_list_frame.rowconfigure(0, weight=1)
assessment_list_frame.columnconfigure(0, weight=1)

# Assessment List Treeview
assessment_list = ttk.Treeview(assessment_list_frame, columns=("ID", "Course ID", "Name", "Due Date"), show='headings')
assessment_list.heading("ID", text="ID")
assessment_list.heading("Course ID", text="Course ID")
assessment_list.heading("Name", text="Name")
assessment_list.heading("Due Date", text="Due Date")

assessment_list.grid(row=0, column=0, sticky='nsew')

assessment_scrollbar = ttk.Scrollbar(assessment_list_frame, orient=tk.VERTICAL, command=assessment_list.yview)
assessment_list.configure(yscroll=assessment_scrollbar.set)
assessment_scrollbar.grid(row=0, column=1, sticky='ns')

# Delete Assessment Button
ttk.Button(assessment_tab, text="Delete Selected Assessment", command=delete_assessment).grid(row=2, column=0, pady=10)

# Show Deleted Assessments Button
ttk.Button(assessment_tab, text="Show Deleted Assessments", command=show_deleted_assessments).grid(row=3, column=0, pady=10)

# Enrollment Management Tab
enrollment_tab = ttk.Frame(notebook)
notebook.add(enrollment_tab, text='Enrollments')

enrollment_tab.columnconfigure(1, weight=1)

# Enrollment Form Frame
enrollment_form_frame = ttk.Frame(enrollment_tab, padding="10 10 10 10")
enrollment_form_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
enrollment_form_frame.columnconfigure(1, weight=1)

ttk.Label(enrollment_form_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
enrollment_student_id_entry = ttk.Entry(enrollment_form_frame)
enrollment_student_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(enrollment_form_frame, text="Course ID:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
enrollment_course_id_entry = ttk.Entry(enrollment_form_frame)
enrollment_course_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(enrollment_form_frame, text="Enrollment Date:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
enrollment_date_entry = ttk.Entry(enrollment_form_frame)
enrollment_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

ttk.Button(enrollment_form_frame, text="Add Enrollment", command=add_enrollment).grid(row=3, columnspan=2, pady=10)

# Enrollment List Frame
enrollment_list_frame = ttk.Frame(enrollment_tab, padding="10 10 10 10")
enrollment_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

enrollment_list_frame.rowconfigure(0, weight=1)
enrollment_list_frame.columnconfigure(0, weight=1)

# Enrollment List Treeview
enrollment_list = ttk.Treeview(enrollment_list_frame, columns=("ID", "Student ID", "Course ID", "Enrollment Date"), show='headings')
enrollment_list.heading("ID", text="ID")
enrollment_list.heading("Student ID", text="Student ID")
enrollment_list.heading("Course ID", text="Course ID")
enrollment_list.heading("Enrollment Date", text="Enrollment Date")

enrollment_list.grid(row=0, column=0, sticky='nsew')

enrollment_scrollbar = ttk.Scrollbar(enrollment_list_frame, orient=tk.VERTICAL, command=enrollment_list.yview)
enrollment_list.configure(yscroll=enrollment_scrollbar.set)
enrollment_scrollbar.grid(row=0, column=1, sticky='ns')

# Delete Enrollment Button
ttk.Button(enrollment_tab, text="Delete Selected Enrollment", command=delete_enrollment).grid(row=2, column=0, pady=10)

# Show Deleted Enrollments Button
ttk.Button(enrollment_tab, text="Show Deleted Enrollments", command=show_deleted_enrollments).grid(row=3, column=0, pady=10)

# Grade Management Tab
grade_tab = ttk.Frame(notebook)
notebook.add(grade_tab, text='Grades')

grade_tab.columnconfigure(1, weight=1)

# Grade Form Frame
grade_form_frame = ttk.Frame(grade_tab, padding="10 10 10 10")
grade_form_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
grade_form_frame.columnconfigure(1, weight=1)

ttk.Label(grade_form_frame, text="Enrollment ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
grade_enrollment_id_entry = ttk.Entry(grade_form_frame)
grade_enrollment_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(grade_form_frame, text="Assessment ID:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
grade_assessment_id_entry = ttk.Entry(grade_form_frame)
grade_assessment_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(grade_form_frame, text="Grade:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
grade_value_entry = ttk.Entry(grade_form_frame)
grade_value_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

ttk.Button(grade_form_frame, text="Add Grade", command=add_grade).grid(row=3, columnspan=2, pady=10)

# Grade List Frame
grade_list_frame = ttk.Frame(grade_tab, padding="10 10 10 10")
grade_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

grade_list_frame.rowconfigure(0, weight=1)
grade_list_frame.columnconfigure(0, weight=1)

# Grade List Treeview
grade_list = ttk.Treeview(grade_list_frame, columns=("ID", "Enrollment ID", "Assessment ID", "Grade"), show='headings')
grade_list.heading("ID", text="ID")
grade_list.heading("Enrollment ID", text="Enrollment ID")
grade_list.heading("Assessment ID", text="Assessment ID")
grade_list.heading("Grade", text="Grade")

grade_list.grid(row=0, column=0, sticky='nsew')

grade_scrollbar = ttk.Scrollbar(grade_list_frame, orient=tk.VERTICAL, command=grade_list.yview)
grade_list.configure(yscroll=grade_scrollbar.set)
grade_scrollbar.grid(row=0, column=1, sticky='ns')

# Delete Grade Button
ttk.Button(grade_tab, text="Delete Selected Grade", command=delete_grade).grid(row=2, column=0, pady=10)

# Show Deleted Grades Button
ttk.Button(grade_tab, text="Show Deleted Grades", command=show_deleted_grades).grid(row=3, column=0, pady=10)

# Instructor Management Tab
instructor_tab = ttk.Frame(notebook)
notebook.add(instructor_tab, text='Instructors')

instructor_tab.columnconfigure(1, weight=1)

# Instructor Form Frame
instructor_form_frame = ttk.Frame(instructor_tab, padding="10 10 10 10")
instructor_form_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
instructor_form_frame.columnconfigure(1, weight=1)

ttk.Label(instructor_form_frame, text="First Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
instructor_first_name_entry = ttk.Entry(instructor_form_frame)
instructor_first_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(instructor_form_frame, text="Last Name:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
instructor_last_name_entry = ttk.Entry(instructor_form_frame)
instructor_last_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(instructor_form_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
instructor_email_entry = ttk.Entry(instructor_form_frame)
instructor_email_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

ttk.Label(instructor_form_frame, text="Phone:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
instructor_phone_entry = ttk.Entry(instructor_form_frame)
instructor_phone_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

ttk.Button(instructor_form_frame, text="Add Instructor", command=add_instructor).grid(row=4, columnspan=2, pady=10)

# Instructor List Frame
instructor_list_frame = ttk.Frame(instructor_tab, padding="10 10 10 10")
instructor_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

instructor_list_frame.rowconfigure(0, weight=1)
instructor_list_frame.columnconfigure(0, weight=1)

# Instructor List Treeview
instructor_list = ttk.Treeview(instructor_list_frame, columns=("ID", "First Name", "Last Name", "Email", "Phone"), show='headings')
instructor_list.heading("ID", text="ID")
instructor_list.heading("First Name", text="First Name")
instructor_list.heading("Last Name", text="Last Name")
instructor_list.heading("Email", text="Email")
instructor_list.heading("Phone", text="Phone")

instructor_list.grid(row=0, column=0, sticky='nsew')

instructor_scrollbar = ttk.Scrollbar(instructor_list_frame, orient=tk.VERTICAL, command=instructor_list.yview)
instructor_list.configure(yscroll=instructor_scrollbar.set)
instructor_scrollbar.grid(row=0, column=1, sticky='ns')

# Delete Instructor Button
ttk.Button(instructor_tab, text="Delete Selected Instructor", command=delete_instructor).grid(row=2, column=0, pady=10)

# Show Deleted Instructors Button
ttk.Button(instructor_tab, text="Show Deleted Instructors", command=show_deleted_instructors).grid(row=3, column=0, pady=10)

# Start the main loop
refresh_courses()
refresh_students()
refresh_assessments()
refresh_enrollments()
refresh_grades()
refresh_instructors()

root.mainloop()
