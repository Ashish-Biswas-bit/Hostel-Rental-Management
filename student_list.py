import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
import os
import shutil
import os,sys
from db_setup import DB_PATH




def fetch_students():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, id, building, room FROM students")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_student_details(student_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, building, room, photo FROM students WHERE id=?", (student_id,))
    student_data = cursor.fetchone()
    cursor.execute("""SELECT district, upazila, union_name, village, father_name, guardian_number, personal_number
                      FROM addresses WHERE student_id=?""", (student_id,))
    address_data = cursor.fetchone()
    conn.close()
    return student_data, address_data

def fetch_payment_history(student_id):
    # Be tolerant: trim whitespace and also try LIKE matching if exact match fails
    sid = str(student_id).strip()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, deposit, due, fine, advance, date
            FROM payment_history
            WHERE TRIM(student_id)=? COLLATE NOCASE
            ORDER BY date DESC
        """, (sid,))
        data = cursor.fetchall()

        # If no rows found, also try a substring match (handles stored IDs with prefixes)
        if not data:
            cursor.execute("""
                SELECT id, deposit, due, fine, advance, date
                FROM payment_history
                WHERE student_id LIKE ?
                ORDER BY date DESC
            """, (f"%{sid}%",))
            data = cursor.fetchall()
    except Exception as e:
        print('Error fetching payment_history:', e)
        data = []
    finally:
        conn.close()
    return data

def fetch_photo_path(student_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT photo FROM students WHERE id=?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] and os.path.exists(result[0]):
        return result[0]
    return None

def fetch_address(student_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT district, upazila, union_name, village, father_name, guardian_number, personal_number
        FROM addresses WHERE student_id=?
    """, (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def update_student(student_id, name, building, room, photo_path=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if photo_path:
        cursor.execute("UPDATE students SET name=?, building=?, room=?, photo=? WHERE id=?",
                       (name, building, room, photo_path, student_id))
    else:
        cursor.execute("UPDATE students SET name=?, building=?, room=? WHERE id=?",
                       (name, building, room, student_id))
    conn.commit()
    conn.close()

def update_address(student_id, district, upazila, union_name, village, father_name, guardian_number, personal_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM addresses WHERE student_id=?", (student_id,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("""
            UPDATE addresses SET district=?, upazila=?, union_name=?, village=?,
            father_name=?, guardian_number=?, personal_number=?
            WHERE student_id=?
        """, (district, upazila, union_name, village, father_name, guardian_number, personal_number, student_id))
    else:
        cursor.execute("""
            INSERT INTO addresses (student_id, district, upazila, union_name, village,
            father_name, guardian_number, personal_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, district, upazila, union_name, village, father_name, guardian_number, personal_number))
    conn.commit()
    conn.close()

class EditStudentWindow(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title(f"Edit Student - ID {student_id}")
        self.geometry("700x500")
        self.student_id = student_id
        self.photo_path = None
        self.original_photo = None

        container = tk.Frame(self)
        container.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Left frame for student info + photo
        left_frame = tk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=(0,20))

        self.photo_label = tk.Label(left_frame, text="No photo", width=150, height=150, bd=2, relief="groove")
        self.photo_label.pack(pady=10)

        tk.Button(left_frame, text="Upload New Photo", command=self.upload_photo).pack(pady=5)

        self.name_entry = self._create_labeled_entry(left_frame, "Name")
        self.building_entry = self._create_labeled_entry(left_frame, "Building")
        self.room_entry = self._create_labeled_entry(left_frame, "Room")

        # Right frame for address info
        right_frame = tk.Frame(container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right_frame, text="--- Address Info ---", font=("Arial", 12, "bold")).pack(pady=10)

        self.district_entry = self._create_labeled_entry(right_frame, "District")
        self.upazila_entry = self._create_labeled_entry(right_frame, "Upazila")
        self.union_entry = self._create_labeled_entry(right_frame, "Union")
        self.village_entry = self._create_labeled_entry(right_frame, "Village")
        self.father_name_entry = self._create_labeled_entry(right_frame, "Father's Name")
        self.guardian_number_entry = self._create_labeled_entry(right_frame, "Guardian Number")
        self.personal_number_entry = self._create_labeled_entry(right_frame, "Personal Number")

        tk.Button(self, text="Save Changes", command=self.save_changes).pack(pady=20)

        self.load_student_data()

    def _create_labeled_entry(self, parent, label_text):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="w").pack(side=tk.LEFT)
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return entry

    def load_student_data(self):
        student_data, address_data = fetch_student_details(self.student_id)
        if student_data:
            name, building, room, photo = student_data
            self.name_entry.insert(0, name)
            self.building_entry.insert(0, building)
            self.room_entry.insert(0, room)
            if photo and os.path.exists(photo):
                self.original_photo = photo
                self.load_photo(photo)

        if address_data:
            fields = [
                self.district_entry, self.upazila_entry, self.union_entry,
                self.village_entry, self.father_name_entry,
                self.guardian_number_entry, self.personal_number_entry
            ]
            for entry, value in zip(fields, address_data):
                entry.insert(0, value or "")

    def load_photo(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((150, 150))
            tkimg = ImageTk.PhotoImage(img)
            self.photo_label.config(image=tkimg, text="")
            self.photo_label.image = tkimg
        except Exception as e:
            self.photo_label.config(text="No photo")
            print("Error loading photo:", e)

    def upload_photo(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        filename = filedialog.askopenfilename(title="Select Photo", filetypes=filetypes)
        if filename:
            self.photo_path = filename
            self.load_photo(filename)

    

    def save_changes(self):
        name = self.name_entry.get().strip()
        building = self.building_entry.get().strip()
        room = self.room_entry.get().strip()
        district = self.district_entry.get().strip()
        upazila = self.upazila_entry.get().strip()
        union_name = self.union_entry.get().strip()
        village = self.village_entry.get().strip()
        father_name = self.father_name_entry.get().strip()
        guardian_number = self.guardian_number_entry.get().strip()
        personal_number = self.personal_number_entry.get().strip()

        if not name or not building or not room:
            messagebox.showwarning("Input Error", "Name, Building, and Room are required.")
            return

        try:
            photo_db_path = self.original_photo
            if self.photo_path and os.path.isfile(self.photo_path):
                dest_dir = os.path.join(os.path.dirname(DB_PATH), "student_images")
                os.makedirs(dest_dir, exist_ok=True)
                ext = os.path.splitext(self.photo_path)[1]
                dest_path = os.path.join(dest_dir, f"{self.student_id}{ext}")
                shutil.copyfile(self.photo_path, dest_path)
                photo_db_path = dest_path

            update_student(self.student_id, name, building, room, photo_db_path)
            update_address(self.student_id, district, upazila, union_name, village, father_name, guardian_number, personal_number)

            messagebox.showinfo("Success", "Student info updated successfully")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {e}")


class StudentListPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        tk.Label(self, text="Student List", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Name", "ID", "Building", "Room", "Payment History", "Address"), show="headings")
        self.tree.column("Name", width=180)
        self.tree.column("ID", width=100)
        self.tree.column("Building", width=100)
        self.tree.column("Room", width=70)
        self.tree.column("Payment History", width=120)
        self.tree.column("Address", width=120)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        self.btn_edit = tk.Button(btn_frame, text="Edit Selected", bg="#2196F3", fg="white", command=self.edit_selected_student)
        self.btn_edit.pack(side=tk.LEFT, padx=10)

        self.btn_delete = tk.Button(btn_frame, text="Delete Selected", bg="red", fg="white", command=self.delete_selected_student)
        self.btn_delete.pack(side=tk.LEFT, padx=10)

        self.tree.bind("<Double-1>", self.on_double_click)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        students = fetch_students()
        for student in students:
            self.tree.insert("", tk.END, values=(*student, "View", "View"))

    def on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        item = self.tree.identify_row(event.y)
        if not item:
            return

        col = self.tree.identify_column(event.x)
        values = self.tree.item(item, "values")
        student_id = values[1]

        if col == '#5':  # Payment History column
            self.show_payment_history(student_id)
        elif col == '#6':  # Address column
            self.show_address(student_id)

    def show_payment_history(self, student_id):
        win = tk.Toplevel(self)
        win.title(f"Payment History - ID {student_id}")
        win.geometry("650x400")
        tk.Label(win, text=f"Payment History for Student ID: {student_id}", font=("Arial", 14)).pack(pady=10)

        table = ttk.Treeview(win, columns=("Deposit", "Due", "Fine", "Advance", "Date"), show='headings')
        for col in table["columns"]:
            table.heading(col, text=col)
            table.column(col, width=100)

        table.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        payments = fetch_payment_history(student_id)
        if payments:
            for p in payments:
                table.insert("", "end", values=p[1:])
        else:
            tk.Label(win, text="No payment history found.", font=("Arial", 12)).pack(pady=10)

    def show_address(self, student_id):
        photo_path = fetch_photo_path(student_id)
        addr = fetch_address(student_id)

        win = tk.Toplevel(self)
        win.title(f"Student Address - ID {student_id}")
        win.geometry("800x450")
        win.configure(bg="white")

        tk.Label(win, text=f"Student ID: {student_id}", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        content = tk.Frame(win, bg="white")
        content.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        table_frame = tk.Frame(content, bg="white")
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Field", "Value")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
        tree.heading("Field", text="Field")
        tree.heading("Value", text="Value")
        tree.column("Field", width=150, anchor="w")
        tree.column("Value", width=300, anchor="w")
        tree.pack(fill=tk.BOTH, expand=True)

        if addr:
            fields_values = [
                ("District", addr[0]),
                ("Upazila", addr[1]),
                ("Union", addr[2]),
                ("Village", addr[3]),
                ("Father's Name", addr[4]),
                ("Guardian Number", addr[5]),
                ("Personal Number", addr[6]),
            ]
        else:
            fields_values = [
                ("District", ""),
                ("Upazila", ""),
                ("Union", ""),
                ("Village", ""),
                ("Father's Name", ""),
                ("Guardian Number", ""),
                ("Personal Number", ""),
            ]

        for field, value in fields_values:
            tree.insert("", "end", values=(field, value))

        photo_frame = tk.Frame(content, bg="white")
        photo_frame.pack(side=tk.RIGHT, padx=20, pady=10, fill=tk.Y)

        photo_label = tk.Label(photo_frame, bg="white", bd=2, relief="groove")
        photo_label.pack(pady=(0, 10))
        photo_label.pack_forget()

        def toggle_photo():
            if photo_label.winfo_ismapped():
                photo_label.pack_forget()
                toggle_btn.config(text="Show Photo")
            else:
                if photo_path and os.path.exists(photo_path):
                    try:
                        img = Image.open(photo_path)
                        img.thumbnail((150, 150))
                        tkimg = ImageTk.PhotoImage(img)
                        photo_label.config(image=tkimg)
                        photo_label.image = tkimg
                        photo_label.pack(pady=(0, 10))
                        toggle_btn.config(text="Hide Photo")
                    except Exception as e:
                        messagebox.showerror("Photo Error", f"Could not load photo:\n{e}")
                else:
                    messagebox.showinfo("No Photo", "No photo available for this student.")

        toggle_btn = tk.Button(photo_frame, text="Show Photo", command=toggle_photo)
        toggle_btn.pack()

    def edit_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a student to edit.")
            return
        student_data = self.tree.item(selected[0], "values")
        student_id = student_data[1]
        EditStudentWindow(self, student_id)

    def delete_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a student to delete.")
            return
        student_data = self.tree.item(selected[0], "values")
        student_id = student_data[1]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student ID {student_id}? This action cannot be undone.")
        if not confirm:
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM addresses WHERE student_id=?", (student_id,))
            cursor.execute("DELETE FROM payment_history WHERE student_id=?", (student_id,))
            cursor.execute("DELETE FROM student_balance WHERE student_id=?", (student_id,))
            cursor.execute("DELETE FROM students WHERE id=?", (student_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", f"Student ID {student_id} deleted successfully.")
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete student: {e}")
