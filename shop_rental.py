import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date
import webbrowser
import os, sys, shutil
from db_setup import DB_PATH
from PIL import Image, ImageTk




class ShopRentalPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")

        tk.Label(self, text="🏬 Flat Rental Management", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.main_frame, bg="#f7f7f7", bd=1, relief=tk.SOLID)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)

        self.setup_shop_table()
        self.setup_payment_form()
        self.setup_add_shop_button()

        self.ensure_tables_exist()
        self.load_shop_list()
        self.auto_adjust_rent_from_advance()
        
        # Create upload folder for renter images
        self.renter_images_folder = os.path.join(os.path.dirname(DB_PATH), "renter_images")
        os.makedirs(self.renter_images_folder, exist_ok=True)
        self.renter_image_path = None

    def ensure_tables_exist(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                shop_no TEXT PRIMARY KEY,
                renter_name TEXT,
                phone TEXT,
                address TEXT,
                advance_balance REAL DEFAULT 0,
                monthly_rent REAL DEFAULT 0,
                renter_image TEXT
            )
        """)
        # ensure shop_payments
        c.execute("""
            CREATE TABLE IF NOT EXISTS shop_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_no TEXT,
                amount REAL,
                date TEXT,
                due REAL DEFAULT 0,
                FOREIGN KEY(shop_no) REFERENCES shops(shop_no)
            )
        """)
        conn.commit()
        conn.close()

    def setup_shop_table(self):
        # Creates the treeview for shop list
        self.tree = ttk.Treeview(self.left_frame, columns=("NID No", "Renter Name", "Phone", "Address"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.open_payment_history)

    def setup_payment_form(self):
        tk.Label(self.right_frame, text="💵 Payment Form", bg="#f7f7f7", font=("Arial", 14, "bold")).pack(pady=10)
        form_frame = tk.Frame(self.right_frame, bg="#f7f7f7")
        form_frame.pack(pady=10)
        tk.Label(form_frame, text="NID No:", bg="#f7f7f7", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.shop_entry = tk.Entry(form_frame, font=("Arial", 10))
        self.shop_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Payment Amount:", bg="#f7f7f7", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = tk.Entry(form_frame, font=("Arial", 10))
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.right_frame, text="Submit Payment", bg="#1abc9c", fg="white", font=("Arial", 11), command=self.submit_payment, width=20).pack(pady=10)
        tk.Button(self.right_frame, text="📢 WhatsApp Reminder", bg="#25D366", fg="white", font=("Arial", 11), command=self.send_whatsapp_reminder, width=20).pack(pady=(0,10))

    def setup_add_shop_button(self):
        tk.Button(self.right_frame, text="➕ Add Flat", bg="#3498db", fg="white", font=("Arial", 11), command=self.open_add_shop_form, width=20).pack(pady=(10,5))

    def open_add_shop_form(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        form = tk.Frame(self.left_frame, bg="white")
        form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        tk.Label(form, text="➕ Add New Flat", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        fields = [("NID No", "shop_no"), ("Renter Name", "renter_name"), ("Address", "address"), ("Phone", "phone"), ("Monthly Rent", "monthly_rent"), ("Advance Paid", "advance_balance")]
        self.shop_entries = {}
        for label, key in fields:
            tk.Label(form, text=label+":" , font=("Arial", 10), bg="white").pack(anchor="w", pady=(8,0))
            entry = tk.Entry(form, font=("Arial", 10))
            entry.pack(fill=tk.X, pady=2)
            self.shop_entries[key] = entry
        tk.Label(form, text="Renter Image:", font=("Arial", 10), bg="white").pack(anchor="w", pady=(8,0))
        img_btn_frame = tk.Frame(form, bg="white")
        img_btn_frame.pack(fill=tk.X, pady=2)
        tk.Button(img_btn_frame, text="📷 Upload Renter Image", bg="#3498db", fg="white", font=("Arial", 10), command=self.upload_renter_image).pack(side=tk.LEFT, padx=5)
        self.renter_image_label = tk.Label(img_btn_frame, text="No image selected", font=("Arial", 9), bg="white", fg="#95a5a6")
        self.renter_image_label.pack(side=tk.LEFT, padx=5)
        tk.Button(form, text="Save", bg="#2ecc71", fg="white", font=("Arial", 11), command=self.save_shop).pack(pady=15)
        tk.Button(form, text="← Back to List", command=self.load_shop_list, bg="#95a5a6", fg="white", font=("Arial", 10)).pack()

    def upload_renter_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=filetypes, title="Select Renter Image")
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.renter_images_folder, filename)
            shutil.copy(file_path, dest_path)
            self.renter_image_path = dest_path
            self.renter_image_label.config(text=f"✓ {filename}", fg="#27ae60")

    def open_payment_history(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "No NID selected!")
            return
        shop_no = self.tree.item(selected_item)['values'][0]
        PaymentHistoryPopup(self.master, shop_no)
    def save_shop(self):
        data = {key: entry.get().strip() for key, entry in self.shop_entries.items()}

        if not all(data.values()):
            messagebox.showwarning("Validation Error", "⚠️ Fill in all the boxes!")
            return

        try:
            advance_balance = float(data["advance_balance"] if data["advance_balance"] else 0)
            monthly_rent = float(data["monthly_rent"])
        except ValueError:
            messagebox.showwarning("Validation Error", "Advance and Monthly Rent must be in numbers!")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shops (shop_no, renter_name, phone, address, advance_balance, monthly_rent, renter_image) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (data['shop_no'], data['renter_name'], data['phone'], data['address'], advance_balance, monthly_rent, self.renter_image_path))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "✅ Flat Added!")
            self.renter_image_path = None
            self.load_shop_list()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "⚠️ NID is already there!")

    def load_shop_list(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        self.setup_shop_table()

        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT shop_no, renter_name, phone, address FROM shops")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

        btn_frame = tk.Frame(self.left_frame, bg="white")
        btn_frame.pack(pady=10)

        edit_btn = tk.Button(btn_frame, text="✏️ Edit Selected", bg="#f39c12", fg="white", font=("Arial", 11),
                             command=self.edit_selected_shop, width=15)
        edit_btn.pack(side=tk.LEFT, padx=5)

        view_btn = tk.Button(btn_frame, text="🔎 View Details", bg="#2980b9", fg="white", font=("Arial", 11),
                             command=self.view_selected_shop, width=15)
        view_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(btn_frame, text="🗑️ Delete Selected", bg="#e74c3c", fg="white", font=("Arial", 11),
                               command=self.delete_selected_shop, width=15)
        delete_btn.pack(side=tk.LEFT, padx=5)





    def edit_selected_shop(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "No flat selected!")
            return

        values = self.tree.item(selected)["values"]
        shop_no = values[0]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT renter_name, address, phone, monthly_rent, advance_balance, renter_image FROM shops WHERE shop_no=?", (shop_no,))
        data = cursor.fetchone()
        conn.close()

        if not data:
            messagebox.showerror("Error", "Flat information not found!")
            return

        # Clear previous UI
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        form = tk.Frame(self.left_frame, bg="#f8f9fa")
        form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        tk.Label(form, text=f"✏️ Edit Flat - {shop_no}", font=("Segoe UI", 16, "bold"), bg="#f8f9fa", fg="#2c3e50")\
            .grid(row=0, column=0, columnspan=2, pady=(0, 15))

    

        fields = [
            ("Renter Name", "renter_name"),
            ("Address", "address"),
            ("Phone", "phone"),
            ("Monthly Rent", "monthly_rent"),
            ("Advance Paid", "advance_balance")
        ]
        self.edit_entries = {}

        for idx, (label, key) in enumerate(fields, start=1):
            tk.Label(form, text=label + ":", font=("Segoe UI", 11), bg="#f8f9fa", anchor="w")\
                .grid(row=idx, column=0, sticky="w", padx=(0, 10), pady=5)
            entry = tk.Entry(form, font=("Segoe UI", 11), relief="solid", bd=1)
            entry.insert(0, str(data[idx - 1]))
            entry.grid(row=idx, column=1, sticky="ew", pady=5, ipady=3)
            self.edit_entries[key] = entry

        # Renter Image Section with Preview
        img_row = len(fields) + 1
        tk.Label(form, text="Renter Image:", font=("Segoe UI", 11), bg="#f8f9fa", anchor="w")\
            .grid(row=img_row, column=0, sticky="w", padx=(0, 10), pady=5)
        
        img_btn_frame = tk.Frame(form, bg="#f8f9fa")
        img_btn_frame.grid(row=img_row, column=1, sticky="ew", pady=5)
        
        self.edit_renter_image_path = data[5]  # Current renter image path
        tk.Button(img_btn_frame, text="📷 Upload Image", bg="#3498db", fg="white", font=("Segoe UI", 10),
                  command=self.upload_edit_renter_image).pack(side=tk.LEFT, padx=5)
        
        self.edit_renter_image_label = tk.Label(img_btn_frame, text=f"✓ {os.path.basename(data[5])}" if data[5] else "No image", 
                                         font=("Segoe UI", 9), bg="#f8f9fa", fg="#27ae60" if data[5] else "#95a5a6")
        self.edit_renter_image_label.pack(side=tk.LEFT, padx=5)
        
        def save_edit():
            updated_data = {key: entry.get().strip() for key, entry in self.edit_entries.items()}

            if not all(updated_data.values()):
                messagebox.showwarning("Validation Error", "⚠️ Fill in all the boxes!")
                return

            try:
                advance_balance = float(updated_data["advance_balance"])
                monthly_rent = float(updated_data["monthly_rent"])
            except ValueError:
                messagebox.showwarning("Validation Error", "Advance and Monthly Rent must be numbers!")
                return

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE shops 
                    SET renter_name=?, address=?, phone=?, monthly_rent=?, advance_balance=?, renter_image=?
                    WHERE shop_no=?
                """, (
                    updated_data["renter_name"],
                    updated_data["address"],
                    updated_data["phone"],
                    monthly_rent,
                    advance_balance,
                    self.edit_renter_image_path,
                    shop_no
                ))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "✅ Flat Updated Successfully!")
                self.load_shop_list()
            except Exception as e:
                messagebox.showerror("Error", f"There was a problem updating!\n{e}")

        # Button Row
        btn_frame = tk.Frame(form, bg="#f8f9fa")
        btn_frame.grid(row=img_row + 1, column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="💾 Save Changes", bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"),
                relief="flat", padx=15, pady=5, command=save_edit)\
            .pack(side="left", padx=5)

        tk.Button(btn_frame, text="← Back", bg="#95a5a6", fg="white", font=("Segoe UI", 11, "bold"),
                relief="flat", padx=15, pady=5, command=self.load_shop_list)\
            .pack(side="left", padx=5)

    def upload_edit_renter_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=filetypes, title="Select Renter Image")
        if file_path:
            # Copy image to renter_images folder
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.renter_images_folder, filename)
            shutil.copy(file_path, dest_path)
            self.edit_renter_image_path = dest_path
            self.edit_renter_image_label.config(text=f"✓ {filename}", fg="#27ae60")


    def view_selected_shop(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "No flat selected!")
            return

        values = self.tree.item(selected)["values"]
        shop_no = values[0]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT renter_name, address, phone, monthly_rent, advance_balance, renter_image FROM shops WHERE shop_no=?", (shop_no,))
        data = cursor.fetchone()
        conn.close()

        if not data:
            messagebox.showerror("Error", "Flat information not found!")
            return

        # Create details window
        win = tk.Toplevel(self.master)
        win.title(f"🔎 Details - {shop_no}")
        win.geometry("480x380")

        info_frame = tk.Frame(win, padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        labels = [
            ("Shop No:", shop_no),
            ("Renter Name:", data[0]),
            ("Address:", data[1]),
            ("Phone:", data[2]),
            ("Monthly Rent:", str(data[3])),
            ("Advance Balance:", str(data[4]))
        ]

        for i, (lbl, val) in enumerate(labels):
            tk.Label(info_frame, text=lbl, font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=4)
            tk.Label(info_frame, text=val, font=("Segoe UI", 10)).grid(row=i, column=1, sticky="w", pady=4)

        # Image preview — resolve stored path robustly and keep reference on the Toplevel
        raw_img_path = data[5]
        img_label = tk.Label(info_frame, bd=1, relief="solid")
        img_label.grid(row=0, column=2, rowspan=6, padx=10, pady=4)

        def resolve_image_path(p):
            # Try multiple fallbacks for stored path
            if not p:
                return None
            candidates = []
            # 1) as-is (maybe absolute)
            candidates.append(p)
            # 2) absolute version
            try:
                candidates.append(os.path.abspath(p))
            except Exception:
                pass
            # 3) relative to DB folder
            try:
                candidates.append(os.path.join(os.path.dirname(DB_PATH), p))
            except Exception:
                pass
            # 4) file name inside renter_images folder
            try:
                candidates.append(os.path.join(self.renter_images_folder, os.path.basename(p)))
            except Exception:
                pass
            # 5) project uploads folder (common in this project)
            try:
                candidates.append(os.path.join(os.path.dirname(__file__), 'uploads', os.path.basename(p)))
            except Exception:
                pass
            # 6) cwd relative
            try:
                candidates.append(os.path.join(os.getcwd(), p))
            except Exception:
                pass

            for c in candidates:
                if not c:
                    continue
                try:
                    if os.path.exists(c):
                        return c
                except Exception:
                    continue
            return None

        found_path = resolve_image_path(raw_img_path)

        if found_path:
            try:
                img = Image.open(found_path)
                img.thumbnail((300, 220))
                # store the PhotoImage on the window so it won't be garbage collected
                win._detail_photo = ImageTk.PhotoImage(img)
                img_label.config(image=win._detail_photo, text="")
                img_label.image = win._detail_photo
            except Exception as e:
                img_label.config(text="Image unavailable")
                print(f"Failed to load image for {shop_no}: {e}")
                # also show attempted path for debugging
                tk.Label(info_frame, text=f"Tried: {found_path}", fg="#c0392b").grid(row=6, column=0, columnspan=3, pady=(6,0))
        else:
            img_label.config(text="No image")
            if raw_img_path:
                tk.Label(info_frame, text=f"Image not found: {raw_img_path}", fg="#c0392b").grid(row=6, column=0, columnspan=3, pady=(6,0))

        tk.Button(win, text="Close", command=win.destroy, bg="#95a5a6", fg="white").pack(pady=8)

    def delete_selected_shop(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "No flat selected!")
            return

        values = self.tree.item(selected)["values"]
        shop_no = values[0]

        answer = messagebox.askyesno("Confirm Delete", f"Do you want to delete flat {shop_no}? This will delete all payment history!")
        if not answer:
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shop_payments WHERE shop_no=?", (shop_no,))
            cursor.execute("DELETE FROM shops WHERE shop_no=?", (shop_no,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "✅ Flat and Payment History have been successfully deleted!")
            self.load_shop_list()
        except Exception as e:
            messagebox.showerror("Error", f"There was a problem deleting!\n{e}")

    def submit_payment(self):
        shop_no = self.shop_entry.get().strip()
        payment_amount_str = self.amount_entry.get().strip()
        date_today = datetime.now().strftime("%Y-%m-%d")

        if not shop_no or not payment_amount_str:
            messagebox.showwarning("Warning", "Fill in all the boxes!")
            return

        try:
            payment_amount = float(payment_amount_str)
        except ValueError:
            messagebox.showwarning("Warning", "Amount must be a number!")
            return  

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # 🔸 Shop info
            cursor.execute("SELECT monthly_rent, advance_balance FROM shops WHERE shop_no=?", (shop_no,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "NID No. not found!")
                return

            monthly_rent, advance_balance = result

            # 🔸 Check unpaid dues of current month (if any)
            cursor.execute("""
                SELECT SUM(due) FROM shop_payments 
                WHERE shop_no=? AND strftime('%Y-%m', date)=strftime('%Y-%m', ?)
            """, (shop_no, date_today))
            existing_due = cursor.fetchone()[0] or 0.0

            # 🔸 Step 1: Total payable including current rent + previous due
            total_due_before_advance = monthly_rent + existing_due

            # 🔸 Step 2: Use advance balance to reduce total_due
            net_due = total_due_before_advance - advance_balance
            net_due = max(0, net_due)  # avoid negative due

            # 🔸 Step 3: Handle payment
            if payment_amount >= net_due:
                due = 0
                new_advance = payment_amount - net_due
            else:
                due = net_due - payment_amount
                new_advance = 0

            # 🔸 Step 4: Update advance balance in shop table
            cursor.execute("UPDATE shops SET advance_balance = ? WHERE shop_no=?", (new_advance, shop_no))

            # 🔸 Step 5: Save payment record
            cursor.execute("""
                INSERT INTO shop_payments (shop_no, amount, date, due) 
                VALUES (?, ?, ?, ?)
            """, (shop_no, payment_amount, date_today, due))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"✅ Payment Submitted!\n🧾 Due: {due:.2f} Tk\n💰 Advance: {new_advance:.2f} Tk")
            self.shop_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"❌ There was a problem submitting the payment!\n{e}")

    def send_whatsapp_reminder(self):
        shop_no = self.shop_entry.get().strip()
        if not shop_no:
            messagebox.showwarning("Warning", "Input NID No!")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT renter_name, phone, monthly_rent FROM shops WHERE shop_no=?", (shop_no,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            messagebox.showerror("Error", "NID No. not found!")
            return

        renter_name, phone, rent = result
        phone = phone.strip().replace(" ", "").replace("+", "")
        if not phone.startswith("880"):
            if phone.startswith("0"):
                phone = "88" + phone
            else:
                phone = "880" + phone

        message = (
            f"Hello, Mr/Mrs. {renter_name},\n\n"
            f"It's time to pay your monthly rent {rent}tk for your NID number {shop_no}.\n"
            f"Please complete the payment within the stipulated time.\n\n"
            f"Thank you for your cooperation.\n"
            f"You can contact me for any assistance.\n\n"
            f"Best regards,\n"
            f"Your Rental Management Team \n\n"
            f"017XXXXXXXX"
        )

        message_encoded = message.replace(" ", "%20").replace("\n", "%0A")
        wa_url = f"https://wa.me/{phone}?text={message_encoded}"

        if messagebox.askyesno("Send WhatsApp?", f"Want to send a WhatsApp message to {renter_name} ({phone})?"):
            webbrowser.open(wa_url)

    def open_payment_history(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "No NID selected!")
            return

        shop_no = self.tree.item(selected_item)['values'][0]
        # Now show a new window with shop_no or fetch history
        PaymentHistoryPopup(self.master, shop_no)

    def auto_adjust_rent_from_advance(self):
        today = date.today()
        if today.day != 10:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT shop_no, advance_balance, monthly_rent FROM shops")
        shops = cursor.fetchall()

        for shop_no, balance, rent in shops:
            cursor.execute("SELECT COUNT(*) FROM shop_payments WHERE shop_no=? AND date>=?", (shop_no, today.strftime("%Y-%m-01")))
            paid_this_month = cursor.fetchone()[0]

            if paid_this_month == 0 and balance >= rent:
                cursor.execute("INSERT INTO shop_payments (shop_no, amount, date, due) VALUES (?, ?, ?, 0)",
                               (shop_no, rent, today.strftime("%Y-%m-%d")))
                cursor.execute("UPDATE shops SET advance_balance = advance_balance - ? WHERE shop_no=?", (rent, shop_no))

        conn.commit()
        conn.close()


class PaymentHistoryPopup(tk.Toplevel):
    def __init__(self, master, shop_no):
        super().__init__(master)
        self.title(f"💳 Payment History - Flat {shop_no}")
        self.geometry("600x400")

        # Treeview Frame + Scrollbar
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, columns=("Date", "Amount", "Due"), show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("Date", text="Date")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Due", text="Due")

        self.tree.column("Date", width=150, anchor="center")
        self.tree.column("Amount", width=120, anchor="center")
        self.tree.column("Due", width=120, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Fetch & Display data
        total_paid = 0
        total_due = 0

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT date, amount, due FROM shop_payments WHERE shop_no=? ORDER BY date DESC", (shop_no,))
        payments = cursor.fetchall()

        for date_, amount, due in payments:
            self.tree.insert("", tk.END, values=(date_, f"৳{amount:.2f}", f"৳{due:.2f}"))
            total_paid += amount
            total_due += due

        cursor.execute("SELECT advance_balance FROM shops WHERE shop_no=?", (shop_no,))
        res = cursor.fetchone()
        advance_balance = res[0] if res else 0.0

        conn.close()

        # Totals Summary
        summary = tk.Frame(self)
        summary.pack(pady=(0, 10))
        # tk.Label(summary, text=f"Total Paid: ৳{total_paid:.2f}", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Label(summary, text=f"Total Due: ৳{total_due:.2f}", font=("Arial", 12, "bold"), fg="red").pack(side=tk.LEFT, padx=10)
        tk.Label(summary, text=f"Advance Balance: ৳{advance_balance:.2f}", font=("Arial", 12, "bold"), fg="#2980b9").pack(side=tk.LEFT, padx=10)