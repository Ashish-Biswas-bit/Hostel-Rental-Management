import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import sqlite3
import os,sys
from db_setup import DB_PATH




def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



PROFILE_IMG = resource_path("assets/logo2.png")
#PROFILE_IMG = "assets/profile.jpg"

def search_students(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, s.id, s.building, s.room,
               IFNULL(SUM(p.due), 0) AS total_due
        FROM students s
        LEFT JOIN student_balance p ON s.id = p.student_id
        WHERE s.name LIKE ? OR s.id LIKE ?
        GROUP BY s.id
    """, (f"%{query}%", f"%{query}%"))

    results = cursor.fetchall()
    conn.close()
    return results


# Renter search
def search_renters(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT shop_no, renter_name, phone, address, monthly_rent FROM shops
        WHERE renter_name LIKE ? OR shop_no LIKE ?
    """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    conn.close()
    return results

class DefaultPage(tk.Frame):
    def __init__(self, parent, search_query=""):
        super().__init__(parent, bg="white")
        self.search_query = search_query

        self.title_label = tk.Label(self, text="Hostel Name- Hostel & Rent Management",
                                    font=("Arial", 18, "bold"), bg="white", fg="#2c3e50")
        self.title_label.pack(pady=(20, 10))

        if search_query:
            self.render_search_results(search_query)
        else:
            self.render_default_profile()

    def render_default_profile(self):
        profile_frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        profile_frame.pack(pady=30, padx=20)

        # Shadow-style effect using an inner frame
        card = tk.Frame(profile_frame, bg="#f9f9f9", bd=1, relief="ridge")
        card.pack(padx=10, pady=10)

        # Round profile image with glow border
        if os.path.exists(PROFILE_IMG):
            round_img = self.get_round_image(PROFILE_IMG, size=(160, 160))
            img_container = tk.Canvas(card, width=170, height=170, bg="#f9f9f9", highlightthickness=0)
            img_container.create_oval(5, 5, 165, 165, fill="#ffffff", outline="#dcdcdc", width=2)
            img_container.create_image(85, 85, image=round_img)
            img_container.image = round_img
            img_container.pack(pady=(15, 10))



        # Name
        tk.Label(card, text="HOSTEL & RENT", font=("Segoe UI", 16, "bold"),
                bg="#f9f9f9", fg="#2c3e50").pack(pady=4)

        # Title
        tk.Label(card, text="Director of ASHISH", font=("Segoe UI", 11, "italic"),
                bg="#f9f9f9", fg="#7f8c8d").pack()

        # Decorative line
        tk.Label(card, text="━" * 25, font=("Arial", 10), bg="#f9f9f9", fg="#ecf0f1").pack(pady=6)

        # Footer
        footer = tk.Label(self, text="© 2025 Hostel Name | Version 1.0 | All rights reserved.",
                        font=("Segoe UI", 9), bg="white", fg="gray")
        footer.pack(side=tk.BOTTOM, pady=6)


    def render_search_results(self, query):
        # === Student Search Results ===
        tk.Label(self, text="🎓 Student Results (Including Due)", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50")\
            .pack(anchor="w", padx=20, pady=(10, 0))

        student_results = search_students(query)

        if student_results:
            student_tree = ttk.Treeview(self, columns=("Name", "ID", "Building", "Room", "Due (৳)"),
                                        show="headings", height=5)
            for col in student_tree["columns"]:
                student_tree.heading(col, text=col)
                student_tree.column(col, width=140, anchor="center")
            student_tree.pack(fill=tk.X, padx=20, pady=5)

            for row in student_results:
                student_tree.insert("", tk.END, values=row)
        else:
            tk.Label(self, text="❌ No Student results found!", font=("Arial", 11), bg="white", fg="red")\
                .pack(padx=20, pady=5, anchor="w")

        # === Renter Search Results ===
        tk.Label(self, text="🏬 Flat Renter Results (Monthly Rent Included)", font=("Arial", 14, "bold"),
                 bg="white", fg="#2c3e50").pack(anchor="w", padx=20, pady=(15, 0))

        renter_results = search_renters(query)

        if renter_results:
            renter_tree = ttk.Treeview(self, columns=("NID No", "Renter Name", "Phone", "Address", "Monthly Rent (৳)"),
                                       show="headings", height=5)
            for col in renter_tree["columns"]:
                renter_tree.heading(col, text=col)
                renter_tree.column(col, width=140, anchor="center")
            renter_tree.pack(fill=tk.X, padx=20, pady=(5, 15))

            for row in renter_results:
                renter_tree.insert("", tk.END, values=row)
        else:
            tk.Label(self, text="❌ No Renter results found!", font=("Arial", 11), bg="white", fg="red")\
                .pack(padx=20, pady=5, anchor="w")

    def get_round_image(self, path, size=(100, 100)):
        img = Image.open(path).resize(size).convert("RGBA")
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask)
        return ImageTk.PhotoImage(img)
