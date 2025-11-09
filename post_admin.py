
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, sqlite3
from db_setup import DB_PATH

import shutil

# Use an absolute uploads folder path relative to this file for reliability
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



class PostAdminPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Get parent's background color
        parent_bg = parent.cget('bg')
        
        # Set the background color
        self.configure(bg=parent_bg)
        
        # Configure the frame to fill the parent and take its background
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, bg=parent_bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Create main frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=parent_bg)
        
        # Configure canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window inside canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas to expand with window
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Configure mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Grid layout for canvas and scrollbar
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Connect canvas and scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.image_path = None
        self.build_ui()
        self.load_ads()
    
    def on_canvas_configure(self, event):
        # Update the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Update the canvas's width to fit the inner frame
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def build_ui(self):
        # Get background color
        bg_color = self.cget('bg')
        
        # Title frame with a different background for visual separation
        title_frame = tk.Frame(self.scrollable_frame, bg="#E8F6F3", padx=15, pady=10)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(title_frame, text="🏠 Post New Rent Ad", font=("Helvetica", 24, "bold"), 
                bg="#E8F6F3", fg="#1A5276").pack()
        
        # Main container for form and list
        self.main_container = tk.Frame(self.scrollable_frame, bg=bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Header Frame
        header_frame = tk.Frame(self.main_container, bg="#E8F6F3", height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Form Container Frame
        form_container = tk.Frame(self.main_container, bg="#DFF3EF", padx=3, pady=3)
        form_container.pack(fill=tk.X, pady=(0, 10))
        
        # Form Frame
        form = tk.Frame(form_container, bg="white", bd=0, padx=15, pady=15)
        form.pack(fill=tk.X)

        # Property Details Section
        details_frame = tk.LabelFrame(form, text=" 🏢 Property Details ", font=("Arial", 12, "bold"), 
                                    bg="white", fg="#2C3E50")
        details_frame.pack(fill=tk.X, pady=(0, 10))

        # Create inner frame for property type and category
        prop_frame = tk.Frame(details_frame, bg="white")
        prop_frame.pack(fill=tk.X, padx=15, pady=10)

        # Property Type
        type_frame = tk.Frame(prop_frame, bg="white")
        type_frame.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(type_frame, text="Property Type:", font=("Arial", 11), bg="white").pack(side=tk.LEFT)
        self.property_type = ttk.Combobox(type_frame, values=["Hostel", "Flat"], 
                        state="readonly", font=("Arial", 11), width=15)
        self.property_type.pack(side=tk.LEFT, padx=(10, 0))
        self.property_type.current(0)

        # Category
        cat_frame = tk.Frame(prop_frame, bg="white")
        cat_frame.pack(side=tk.LEFT)
        tk.Label(cat_frame, text="Category:", font=("Arial", 11), bg="white").pack(side=tk.LEFT)
        self.category = ttk.Combobox(cat_frame, values=["Single", "Shared", "Family", "Studio"], 
                    state="readonly", font=("Arial", 11), width=15)
        self.category.pack(side=tk.LEFT, padx=(10, 0))
        self.category.current(0)

        # Gender
        gender_frame = tk.Frame(prop_frame, bg="white")
        gender_frame.pack(side=tk.LEFT, padx=(20, 0))
        tk.Label(gender_frame, text="Gender:", font=("Arial", 11), bg="white").pack(side=tk.LEFT)
        self.gender = ttk.Combobox(gender_frame, values=["Male", "Female", "Any"], 
                    state="readonly", font=("Arial", 11), width=10)
        self.gender.pack(side=tk.LEFT, padx=(10, 0))
        self.gender.current(2)

        # Main Information Section
        info_frame = tk.LabelFrame(form, text=" 📝 Main Information ", font=("Arial", 12, "bold"),
                                 bg="white", fg="#2C3E50")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Inner frame for content
        info_content = tk.Frame(info_frame, bg="white")
        info_content.pack(fill=tk.X, padx=15, pady=10)

        # Title
        title_frame = tk.Frame(info_content, bg="white")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, text="Ad Title*:", font=("Arial", 11), bg="white", width=12, anchor="w").pack(side=tk.LEFT)
        self.title_entry = tk.Entry(title_frame, font=("Arial", 11))
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Rent and Location row
        rent_loc_frame = tk.Frame(info_content, bg="white")
        rent_loc_frame.pack(fill=tk.X, pady=(0, 10))

        # Rent
        tk.Label(rent_loc_frame, text="Rent (৳)*:", font=("Arial", 11), bg="white", width=12, anchor="w").pack(side=tk.LEFT)
        self.rent_entry = tk.Entry(rent_loc_frame, font=("Arial", 11), width=20)
        self.rent_entry.pack(side=tk.LEFT)

        # Location
        tk.Label(rent_loc_frame, text="Location*:", font=("Arial", 11), bg="white", width=12, anchor="w").pack(side=tk.LEFT, padx=(20, 0))
        self.location_entry = tk.Entry(rent_loc_frame, font=("Arial", 11))
        self.location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Description
        desc_frame = tk.Frame(info_content, bg="white")
        desc_frame.pack(fill=tk.X)
        
        tk.Label(desc_frame, text="Description:", font=("Arial", 11), bg="white", width=12, anchor="nw").pack(side=tk.LEFT)
        self.desc_text = tk.Text(desc_frame, height=4, font=("Arial", 11), wrap="word")
        self.desc_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Contact Information Section
        contact_frame = tk.LabelFrame(form, text=" 📞 Contact Information ", font=("Arial", 12, "bold"),
                                    bg="white", fg="#2C3E50")
        contact_frame.pack(fill=tk.X, pady=(0, 10))

        # Inner frame for contact details
        contact_content = tk.Frame(contact_frame, bg="white")
        contact_content.pack(fill=tk.X, padx=15, pady=10)

        # Phone
        phone_frame = tk.Frame(contact_content, bg="white")
        phone_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(phone_frame, text="Phone*:", font=("Arial", 11), bg="white", width=12, anchor="w").pack(side=tk.LEFT)
        self.phone_entry = tk.Entry(phone_frame, font=("Arial", 11))
        self.phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Email
        email_frame = tk.Frame(contact_content, bg="white")
        email_frame.pack(fill=tk.X, pady=5)
        tk.Label(email_frame, text="Email:", font=("Arial", 11), bg="white", width=12, anchor="w").pack(side=tk.LEFT)
        self.email_entry = tk.Entry(email_frame, font=("Arial", 11))
        self.email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # WhatsApp
        whatsapp_frame = tk.Frame(contact_content, bg="white")
        whatsapp_frame.pack(fill=tk.X, pady=5)
        tk.Label(whatsapp_frame, text="WhatsApp:", font=("Arial", 11), bg="white", width=12, anchor="w").pack(side=tk.LEFT)
        self.whatsapp_entry = tk.Entry(whatsapp_frame, font=("Arial", 11))
        self.whatsapp_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Image Upload Section
        image_frame = tk.LabelFrame(form, text=" 📸 Property Image ", font=("Arial", 12, "bold"),
                                  bg="white", fg="#2C3E50")
        image_frame.pack(fill=tk.X, pady=(0, 10))

        # Inner frame for image upload
        image_content = tk.Frame(image_frame, bg="white")
        image_content.pack(fill=tk.X, padx=15, pady=10)
        
        upload_btn = tk.Button(image_content, text="Upload Image", command=self.upload_image,
                             bg="#1ABC9C", fg="white", font=("Arial", 11, "bold"),
                             padx=15, pady=5, cursor="hand2")
        upload_btn.pack(side=tk.LEFT)
        
        self.image_label = tk.Label(image_content, text="No image selected", bg="white",
                                  fg="#117A65", font=("Arial", 11))
        self.image_label.pack(side=tk.LEFT, padx=(10, 0))

        # Submit Button Section
        button_frame = tk.Frame(form, bg="white")
        button_frame.pack(fill=tk.X, pady=15)
        
        self.submit_button = tk.Button(button_frame, text="✅ Submit Ad",
                                     command=self.submit_ad, bg="#2E86C1", fg="white",
                                     font=("Arial", 12, "bold"), padx=30, pady=10,
                                     relief="flat", cursor="hand2")
        self.submit_button.pack(side=tk.RIGHT)

        # All Ads Section
        list_frame = tk.LabelFrame(self.main_container, text=" 📋 All Posted Ads ", font=("Arial", 12, "bold"),
                                 bg="white", fg="#2C3E50")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tree frame with scrollbars
        self.tree_frame = tk.Frame(list_frame, bg="white")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Create tree view with scrollbars
        tree_scroll_y = ttk.Scrollbar(self.tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("ID", "Type", "Category", "Gender", "Title", "Rent", "Location", "Contact")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings",
                                yscrollcommand=tree_scroll_y.set,
                                xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        # Make the tree view take up all available space
        self.tree.pack(fill=tk.BOTH, expand=True)
        # Configure column headings and widths
        col_widths = {
            "ID": 60, "Type": 100, "Category": 100, "Gender": 80,
            "Title": 200, "Rent": 100, "Location": 150,
            "Contact": 200
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=col_widths.get(col, 120))
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
            # Save a web-friendly relative path to the DB (served at /static/...)
            self.image_path = os.path.join("static", "uploads", filename).replace('\\\\','/')
            self.image_label.config(text=filename)

    def submit_ad(self):
        title = self.title_entry.get().strip()
        ad_type = self.property_type.get()
        rent = self.rent_entry.get().strip()
        location = self.location_entry.get().strip()
        description = self.desc_text.get("1.0", "end").strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        whatsapp = self.whatsapp_entry.get().strip()
        gender = self.gender.get()

        if not all([title, rent, location, phone]):
            messagebox.showerror("Error", "Please fill all required fields! (Phone is required)")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # Create table with all needed columns
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                category TEXT,
                gender TEXT,
                title TEXT,
                rent TEXT,
                location TEXT,
                description TEXT,
                image_path TEXT,
                phone TEXT,
                email TEXT,
                whatsapp TEXT
            )
        """)
        # safe attempt to add columns for older DBs
        for col in ["category", "gender", "phone", "email", "whatsapp"]:
            try:
                cur.execute(f"ALTER TABLE ads ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:
                pass

        cur.execute("""
            INSERT INTO ads (
                type, category, gender, title, rent, location, description, 
                image_path, phone, email, whatsapp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ad_type, self.category.get(), gender, title, rent, location, description,
            self.image_path, phone, email, whatsapp
        ))
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
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.whatsapp_entry.delete(0, "end")
        self.image_label.config(text="")
        self.image_path = None
        self.submit_button.config(text="✅ Submit Ad", command=self.submit_ad)
        try:
            self.category.current(0)
        except Exception:
            pass

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

        # Load ads with contact info
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        cur.execute("""
            SELECT 
                id, type, category, gender, title, rent, location,
                CASE 
                    WHEN phone != '' AND (email != '' OR whatsapp != '') 
                    THEN phone || ' / ' || COALESCE(email, whatsapp)
                    ELSE COALESCE(phone, email, whatsapp, 'No contact')
                END as contact_info
            FROM ads 
            ORDER BY id DESC
        """)
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
        cur.execute("""
            SELECT type, category, gender, title, rent, location, description, 
                   image_path, phone, email, whatsapp 
            FROM ads WHERE id=?
        """, (ad_id,))
        ad = cur.fetchone()
        conn.close()

        if not ad:
            return

        # Populate form
        self.property_type.set(ad[0])
        if hasattr(self, 'category'):
            try:
                self.category.set(ad[1] or "Single")
            except:
                pass
        if hasattr(self, 'gender'):
            try:
                self.gender.set(ad[2] or "Any")
            except:
                pass
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, ad[3])
        self.rent_entry.delete(0, "end")
        self.rent_entry.insert(0, ad[4])
        self.location_entry.delete(0, "end")
        self.location_entry.insert(0, ad[5])
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", ad[6])
        self.image_path = ad[7]
        self.image_label.config(text=os.path.basename(ad[7]) if ad[7] else "")
        # Contact info
        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, ad[8] or "")
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, ad[9] or "")
        self.whatsapp_entry.delete(0, "end")
        self.whatsapp_entry.insert(0, ad[10] or "")

        # Change submit button to update
        self.submit_button.config(text="💾 Update Ad", command=lambda: self.update_ad(ad_id))

    def update_ad(self, ad_id):
        title = self.title_entry.get().strip()
        ad_type = self.property_type.get()
        rent = self.rent_entry.get().strip()
        location = self.location_entry.get().strip()
        description = self.desc_text.get("1.0", "end").strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        whatsapp = self.whatsapp_entry.get().strip()
        gender = self.gender.get()

        if not all([title, rent, location, phone]):
            messagebox.showerror("Error", "Please fill all required fields! (Phone is required)")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # Ensure columns exist
        for col in ["category", "gender", "phone", "email", "whatsapp"]:
            try:
                cur.execute(f"ALTER TABLE ads ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:
                pass

        cur.execute("""
            UPDATE ads
            SET type=?, category=?, gender=?, title=?, rent=?, location=?, description=?, 
                image_path=?, phone=?, email=?, whatsapp=?
            WHERE id=?
        """, (
            ad_type, self.category.get(), gender, title, rent, location, description,
            self.image_path, phone, email, whatsapp,
            ad_id
        ))
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
