import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import sys, os
from db_setup import DB_PATH



class PaymentPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        tk.Label(self, text="Student Payment", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

        frame = tk.Frame(self, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(frame, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.student_tree = ttk.Treeview(left_frame, columns=("Name", "ID"), show='headings', height=20)
        self.student_tree.heading("Name", text="Name")
        self.student_tree.heading("ID", text="Student ID")
        self.student_tree.pack()

        self.load_students()

        right_frame = tk.Frame(frame, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right_frame, text="Student ID:", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_id = tk.Entry(right_frame)
        self.entry_id.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(right_frame, text="Deposit:", bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_deposit = tk.Entry(right_frame)
        self.entry_deposit.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(right_frame, text="Monthly Payment:", bg="white").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_monthly = tk.Entry(right_frame)
        self.entry_monthly.grid(row=2, column=1, padx=10, pady=5)

        self.btn_submit = tk.Button(right_frame, text="Submit", bg="#2196F3", fg="white", command=self.submit_payment)
        self.btn_submit.grid(row=4, column=1, padx=10, pady=15, sticky="e")

    def load_students(self):
        self.student_tree.delete(*self.student_tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, id FROM students")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            self.student_tree.insert("", tk.END, values=row)

    def submit_payment(self):
        student_id = self.entry_id.get().strip()
        deposit = self.entry_deposit.get().strip()
        monthly_payment = self.entry_monthly.get().strip()
        date_str = datetime.now().strftime("%Y-%m-%d")

        try:
            deposit = float(deposit)
            monthly_payment = float(monthly_payment)
        except:
            messagebox.showerror("Error", "Deposit and Monthly Payment must be numbers.")
            return

        today = datetime.now().day
        fine = (today - 10) * 10 if today > 10 else 0

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            deposit REAL,
            due REAL,
            fine REAL,
            date TEXT,
            advance REAL DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS student_balance (
            student_id TEXT PRIMARY KEY,
            due REAL DEFAULT 0,
            
            advance REAL DEFAULT 0
        )""")

        cursor.execute("PRAGMA table_info(student_balance)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'fine' not in columns:
            cursor.execute("ALTER TABLE student_balance ADD COLUMN fine REAL DEFAULT 0")

        cursor.execute("SELECT due, fine, advance FROM student_balance WHERE student_id=?", (student_id,))
        row = cursor.fetchone()
        prev_due, prev_fine, prev_advance = row if row else (0.0, 0.0, 0.0)

        total_due = prev_due + prev_fine + monthly_payment
        net_due = total_due - prev_advance

        if deposit < net_due:
            new_due = net_due - deposit
            new_advance = 0
        else:
            new_due = 0
            new_advance = deposit - net_due

        cursor.execute("""INSERT INTO payment_history (student_id, deposit, due, fine, date, advance)
                          VALUES (?, ?, ?, ?, ?, ?)""",
                       (student_id, deposit, new_due, fine, date_str, new_advance))

        cursor.execute("""INSERT OR REPLACE INTO student_balance (student_id, due, fine, advance)
                          VALUES (?, ?, ?, ?)""",
                       (student_id, new_due, 0, new_advance))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"✅ Payment saved!\n📌 Total Due (before): {net_due:.2f} Tk\n🧾 Fine this month: {fine} Tk\n💰 Advance: {new_advance:.2f} Tk")

        self.entry_id.delete(0, tk.END)
        self.entry_deposit.delete(0, tk.END)
        self.entry_monthly.delete(0, tk.END)
