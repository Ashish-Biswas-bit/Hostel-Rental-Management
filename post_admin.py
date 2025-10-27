
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, sqlite3
from db_setup import DB_PATH

import shutil
import os

UPLOAD_FOLDER = os.path.join("static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def upload_image(self):
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if path:
        filename = os.path.basename(path)
        dest = os.path.join(UPLOAD_FOLDER, filename)
        shutil.copy(path, dest)  # Copy selected image to static/uploads
        self.image_path = os.path.join("static", "uploads", filename)
        self.image_label.config(text=filename)


class PostAdminPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#E8F6F3")

        self.image_path = None
        self.build_ui()
        self.load_ads()

    def build_ui(self):
        tk.Label(self, text="🏠 Post New Rent Ad", font=("Helvetica", 22, "bold"), bg="#E8F6F3", fg="#1A5276").pack(pady=(0, 20))

        form = tk.Frame(self, bg="white", bd=2, relief="groove")
        form.pack(fill=tk.X, pady=10, ipadx=10, ipady=10)

        # --- Property Type ---
        tk.Label(form, text="Property Type:", font=("Arial", 13), bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.property_type = ttk.Combobox(form, values=["Hostel", "Flat"], state="readonly", font=("Arial", 12))
        self.property_type.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.property_type.current(0)

        # --- Title ---
        tk.Label(form, text="Ad Title:", font=("Arial", 13), bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.title_entry = tk.Entry(form, font=("Arial", 12))
        self.title_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # --- Rent ---
        tk.Label(form, text="Rent (৳):", font=("Arial", 13), bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.rent_entry = tk.Entry(form, font=("Arial", 12))
        self.rent_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # --- Location ---
        tk.Label(form, text="Location:", font=("Arial", 13), bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.location_entry = tk.Entry(form, font=("Arial", 12))
        self.location_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # --- Description ---
        tk.Label(form, text="Description:", font=("Arial", 13), bg="white").grid(row=4, column=0, padx=10, pady=10, sticky="nw")
        self.desc_text = tk.Text(form, height=4, font=("Arial", 12), wrap="word")
        self.desc_text.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        # --- Image Upload ---
        tk.Button(form, text="📸 Upload Image", command=self.upload_image, bg="#1ABC9C", fg="white", font=("Arial", 12, "bold")).grid(row=5, column=0, padx=10, pady=10)
        self.image_label = tk.Label(form, text="", bg="white", fg="#117A65")
        self.image_label.grid(row=5, column=1, sticky="w", padx=10)

        # --- Submit Ad Button ---
        self.submit_button = tk.Button(form, text="✅ Submit Ad", command=self.submit_ad, bg="#2E86C1", fg="white", font=("Arial", 13, "bold"))
        self.submit_button.grid(row=6, column=1, pady=20, sticky="e")

        # --- All Ads Section ---
        tk.Label(self, text="📋 All Posted Ads", font=("Helvetica", 18, "bold"), bg="#E8F6F3", fg="#117864").pack(pady=10)

        self.tree_frame = tk.Frame(self, bg="white")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("ID", "Type", "Title", "Rent", "Location")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- Right-click menu for Edit/Delete ---
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Edit", command=self.edit_selected_ad)
        self.menu.add_command(label="Delete", command=self.delete_selected_ad)
        self.tree.bind("<Button-3>", self.show_menu)

    # --- Functions ---
    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if path:
            filename = os.path.basename(path)
            dest = os.path.join(UPLOAD_FOLDER, filename)
            shutil.copy(path, dest)  # Copy selected image to static/uploads
            self.image_path = dest  # DB তে save করার জন্য
            self.image_label.config(text=filename)

    def submit_ad(self):
        title = self.title_entry.get().strip()
        ad_type = self.property_type.get()
        rent = self.rent_entry.get().strip()
        location = self.location_entry.get().strip()
        description = self.desc_text.get("1.0", "end").strip()

        if not title or not rent or not location:
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                title TEXT,
                rent TEXT,
                location TEXT,
                description TEXT,
                image_path TEXT
            )
        """)
        cur.execute("INSERT INTO ads (type, title, rent, location, description, image_path) VALUES (?, ?, ?, ?, ?, ?)",
                    (ad_type, title, rent, location, description, self.image_path))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Your ad has been posted successfully!")
        self.clear_form()
        self.load_ads()

    def clear_form(self):
        self.title_entry.delete(0, "end")
        self.rent_entry.delete(0, "end")
        self.location_entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")
        self.image_label.config(text="")
        self.image_path = None
        self.submit_button.config(text="✅ Submit Ad", command=self.submit_ad)

    def load_ads(self):
        # Ensure table exists
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                title TEXT,
                rent TEXT,
                location TEXT,
                description TEXT,
                image_path TEXT
            )
        """)
        conn.commit()

        # Load ads
        for i in self.tree.get_children():
            self.tree.delete(i)
        cur.execute("SELECT id, type, title, rent, location FROM ads ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    # --- Right-click menu ---
    def show_menu(self, event):
        selected = self.tree.identify_row(event.y)
        if selected:
            self.tree.selection_set(selected)
            self.menu.post(event.x_root, event.y_root)

    def get_selected_ad_id(self):
        selected = self.tree.selection()
        if selected:
            return self.tree.item(selected[0])['values'][0]  # ID
        return None

    def edit_selected_ad(self):
        ad_id = self.get_selected_ad_id()
        if not ad_id:
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT type, title, rent, location, description, image_path FROM ads WHERE id=?", (ad_id,))
        ad = cur.fetchone()
        conn.close()

        if not ad:
            return

        # Populate form
        self.property_type.set(ad[0])
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, ad[1])
        self.rent_entry.delete(0, "end")
        self.rent_entry.insert(0, ad[2])
        self.location_entry.delete(0, "end")
        self.location_entry.insert(0, ad[3])
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", ad[4])
        self.image_path = ad[5]
        self.image_label.config(text=os.path.basename(ad[5]) if ad[5] else "")

        # Change submit button to update
        self.submit_button.config(text="💾 Update Ad", command=lambda: self.update_ad(ad_id))

    def update_ad(self, ad_id):
        title = self.title_entry.get().strip()
        ad_type = self.property_type.get()
        rent = self.rent_entry.get().strip()
        location = self.location_entry.get().strip()
        description = self.desc_text.get("1.0", "end").strip()

        if not title or not rent or not location:
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            UPDATE ads
            SET type=?, title=?, rent=?, location=?, description=?, image_path=?
            WHERE id=?
        """, (ad_type, title, rent, location, description, self.image_path, ad_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Ad updated successfully!")
        self.clear_form()
        self.load_ads()

    def delete_selected_ad(self):
        ad_id = self.get_selected_ad_id()
        if not ad_id:
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this ad?"):
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM ads WHERE id=?", (ad_id,))
            conn.commit()
            conn.close()
            self.load_ads()
