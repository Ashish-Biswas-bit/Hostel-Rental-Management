import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3, os, shutil
from datetime import datetime
from PIL import Image, ImageTk
import sys
from db_setup import DB_PATH


# ✅ Fixed: Create a persistent path in user's home folder


# ✅ Image directory for student photos
IMG_DIR = os.path.join(os.path.dirname(DB_PATH), "student_images")
os.makedirs(IMG_DIR, exist_ok=True)


class AddStudentPanel(tk.Frame):
    def __init__(self, master, on_save_callback=None):
        super().__init__(master, bg="white")
        self.on_save_callback = on_save_callback
        self.photo_path = ""
        self.tkimg = None  # prevent garbage collection

        # Header with title and photo
        header = tk.Frame(self, bg="#2c3e50")
        header.pack(fill=tk.X, padx=20, pady=(50, 10))

        tk.Label(header, text="📋 Student Admission Form", font=("Arial", 16, "bold"), bg="white").pack(side=tk.LEFT)

        self.img_label = tk.Label(header, bg="white")
        self.img_label.pack(side=tk.RIGHT, padx=10)

        tk.Button(header, text="📸 Upload Photo", command=self.upload_photo, bg="#2196F3", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)

        # Form area
        self.form_frame = tk.Frame(self, bg="white")
        self.form_frame.pack(padx=20, pady=30, fill="both", expand=False)

        self.entries = {}
        fields = [
            "Student Name", "Student ID", "Building", "Room",
            "District", "Upazila", "Union", "Village",
            "Father's Name", "Guardian Number", "Personal Number", "Admission Fee"
        ]

        for i, field in enumerate(fields):
            row, col = divmod(i, 2)
            label = tk.Label(self.form_frame, text=field, bg="white", anchor="w", font=("Arial", 10))
            label.grid(row=row, column=col*2, padx=5, pady=6, sticky="w")

            entry = tk.Entry(self.form_frame, width=25, font=("Arial", 10))
            entry.grid(row=row, column=col*2+1, padx=(0, 15), pady=6, sticky="ew")

            self.entries[field] = entry
            self.form_frame.columnconfigure(col*2+1, weight=1)

        # Submit button
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=(10, 10))

        tk.Button(
            btn_frame,
            text="➕ Save",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=6,
            command=self.save_student
        ).pack()

    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if path:
            self.photo_path = path
            img = Image.open(path)
            img.thumbnail((100, 100))
            self.tkimg = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self.tkimg)
            self.img_label.image = self.tkimg  # keep reference

    def save_student(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}

        # Validation
        if not self.photo_path:
            messagebox.showwarning("Validation Error", "❗ Please upload photo!")
            return

        if not all([data["Student Name"], data["Student ID"], data["Building"], data["Room"], data["Personal Number"], data["Admission Fee"]]):
            messagebox.showwarning("Validation Error", "❗ Important fields cannot be left blank!")
            return

        try:
            fee = float(data["Admission Fee"])
            if fee < 500:
                messagebox.showwarning("Validation Error", "❗ Admission Fee must be 500 taka or more!")
                return
        except ValueError:
            messagebox.showwarning("Validation Error", "Admission Fee must be a valid number!")
            return

        try:
            img_filename = ""
            if self.photo_path:
                ext = os.path.splitext(self.photo_path)[-1]
                img_filename = os.path.join(IMG_DIR, f"{data['Student ID']}{ext}")
                shutil.copy(self.photo_path, img_filename)

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute("""CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY, name TEXT, building TEXT, room TEXT, photo TEXT)""")
            c.execute("""CREATE TABLE IF NOT EXISTS addresses (
                student_id TEXT PRIMARY KEY, district TEXT, upazila TEXT, union_name TEXT,
                village TEXT, father_name TEXT, guardian_number TEXT, personal_number TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id))""")
            c.execute("""CREATE TABLE IF NOT EXISTS admission_fee (
                student_id TEXT PRIMARY KEY, amount REAL, date TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id))""")

            c.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)", (
                data["Student ID"], data["Student Name"], data["Building"], data["Room"], img_filename))

            c.execute("INSERT INTO addresses VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                data["Student ID"], data["District"], data["Upazila"], data["Union"],
                data["Village"], data["Father's Name"], data["Guardian Number"], data["Personal Number"]))

            date = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO admission_fee VALUES (?, ?, ?)",
                      (data["Student ID"], fee, date))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "✅ Student added successfully!")

            if self.on_save_callback:
                self.on_save_callback()

            # Clear all
            for e in self.entries.values():
                e.delete(0, tk.END)
            self.img_label.configure(image='')
            self.photo_path = ""

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "⚠️ Student ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error: {e}")
