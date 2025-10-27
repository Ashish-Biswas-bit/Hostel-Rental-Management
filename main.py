# import tkinter as tk
# from tkinter import ttk
# from PIL import Image, ImageTk
# import os, sys
# import sqlite3
# from student_list import StudentListPanel
# from payment_panel import PaymentPanel
# from add_student import AddStudentPanel
# from shop_rental import ShopRentalPanel
# from default_page import DefaultPage 
# from post_admin import PostAdminPanel
# from ads_booking import BookingPanel


# from db_setup import create_tables_if_not_exist, ensure_photo_column, DB_PATH

# print("DB Path in main.py:", DB_PATH)




# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except AttributeError:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)







# class SplashScreen(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Loading...")
#         self.geometry("600x350")
#         self.configure(bg="#f8fffd")
#         self.overrideredirect(True)  # Remove window borders

#         # Center the window
#         x = (self.winfo_screenwidth() // 2) - (600 // 2)
#         y = (self.winfo_screenheight() // 2) - (350 // 2)
#         self.geometry(f"600x350+{x}+{y}")

#         main_frame = tk.Frame(self, bg="#2F7688", bd=2, relief="groove")
#         main_frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=300)

#         try:
#            # img = Image.open("assets/logo_image.png")
#             img =Image.open(resource_path("assets/logo2.png"))
#             img = img.resize((80, 80))
#             self.logo_img = ImageTk.PhotoImage(img)
#             tk.Label(main_frame, image=self.logo_img, bg="#2F7688").pack(pady=(20, 10))
#         except:
#             tk.Label(main_frame, text="[Logo]", font=("Arial", 16), bg="#2F7688", fg="#5fe0d7").pack(pady=(20, 10))

#         tk.Label(main_frame, text="Hostel & Rent Management", font=("Helvetica", 20, "bold"), bg="#2F7688", fg="#080808").pack()

#         self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
#         self.progress.pack(pady=10)
#         self.progress.start(15)  # Ashish

#         tk.Label(main_frame, text="Loading Application....", font=("Arial", 12), bg="#2F7688", fg="#313535").pack()

#         # Instead of directly destroying, stop progress first
#         self.after(3000, self.close_splash)

#     def close_splash(self):
#         self.progress.stop()  # Stop the progress bar animation
#         self.destroy()        # Then destroy the splash window


# # === MAIN DASHBOARD ===
# class AdminPanel(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Hostel Name Admin Panel")
#         self.geometry("1200x700")
#         self.configure(bg="white")

#                 # Sidebar frame
#         self.sidebar_outer = tk.Frame(self, bg="#2F7688", width=250)
#         self.sidebar_outer.pack(side=tk.LEFT, fill=tk.Y)

#         # Canvas inside sidebar
#         self.sidebar_canvas = tk.Canvas(self.sidebar_outer, bg="#2F7688", width=250, highlightthickness=0)
#         self.sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         # Scrollbar for sidebar
#         self.sidebar_scrollbar = tk.Scrollbar(self.sidebar_outer, orient=tk.VERTICAL, command=self.sidebar_canvas.yview)
#         self.sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

#         self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)

#         # Frame inside canvas to hold buttons
#         self.sidebar = tk.Frame(self.sidebar_canvas, bg="#2F7688")
#         self.sidebar_canvas.create_window((0,0), window=self.sidebar, anchor="nw")

#         # Update scroll region whenever widgets are added
#         def on_frame_configure(event):
#             self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))

#         self.sidebar.bind("<Configure>", on_frame_configure)


#         # Layout: Sidebar and content
#         self.sidebar = tk.Frame(self, bg="#2F7688", width=250)
#         self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

#         self.content_frame = tk.Frame(self, bg="#2F7688")
#         self.content_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

#         # Sidebar logo
#         try:
            
#             logo_img = Image.open(resource_path("assets/logo2.png"))
#             logo_img = logo_img.resize((120, 120))
#             self.logo = ImageTk.PhotoImage(logo_img)
#             tk.Label(self.sidebar, image=self.logo, bg="#2F7688").pack(pady=10)
#         except:
#             tk.Label(self.sidebar, text="[Logo]", font=("Arial", 24, "bold"), bg="#2F7688", fg="white").pack(pady=10)

#         # Sidebar buttons
#         def create_sidebar_btn(text, command):
#             return tk.Button(self.sidebar, text=text, font=("Arial", 14), width=20, pady=10, command=command,
#                              bg="#2297B4", fg="white", activebackground="#9FA7A9", bd=0, cursor="hand2")

#         create_sidebar_btn("🏫 Student List", self.load_student_list).pack(pady=5)
#         create_sidebar_btn("💳 Payment", self.load_payment).pack(pady=5)
#         create_sidebar_btn("➕ Add Student", self.load_add_student).pack(pady=5)
#         create_sidebar_btn("🏬 Flat Rental", self.load_shop_rental).pack(pady=5)
#         create_sidebar_btn("🅰️ Post Ads", self.load_post_admin).pack(pady=5)
#         create_sidebar_btn("💰 Online Renter", self.show_booking_panel).pack(pady=5)


#         # --- Search bar below the buttons ---
#         search_frame = tk.Frame(self.sidebar, bg="#2F7688")
#         search_frame.pack(pady=20, padx=10, fill=tk.X)

#         tk.Label(search_frame, text="Search by Name or ID:", font=("Arial", 12), bg="#099f95", fg="white").pack(anchor="w")

#         self.search_var = tk.StringVar()
#         search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 12))
#         search_entry.pack(pady=5, fill=tk.X)
#         search_entry.bind("<Return>", lambda event: self.perform_search())

#         search_btn = tk.Button(search_frame, text="Search", command=self.perform_search, bg="#1abc9c", fg="white")
#         search_btn.pack(fill=tk.X)

#         # Show default screen initially
#         self.load_default_page()

#      # Refresh button (UI reload)
#         refresh_btn = tk.Button(search_frame, text="⟳ Refresh",
#                                 bg="#3498db", fg="white",
#                                 font=("Arial", 12, "bold"),
#                                 command=self.refresh_ui)
#         refresh_btn.pack(fill=tk.X ,pady=(30, 0))

#         # Load default page initially
#         self.load_default_page()

#     def refresh_ui(self):
#         """Reload the current screen and data without restarting the app."""
#         self.clear_content()
#         self.load_default_page()

#     def clear_content(self):
#         for widget in self.content_frame.winfo_children():
#             widget.destroy()

#     def load_student_list(self):
#         self.clear_content()
#         StudentListPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

#     def load_payment(self):
#         self.clear_content()
#         PaymentPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

#     def load_add_student(self):
#         self.clear_content()
#         AddStudentPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

#     def load_shop_rental(self):
#         self.clear_content()
#         ShopRentalPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

#     def perform_search(self):
#         query = self.search_var.get().strip()
#         self.load_default_page(search_query=query)

#     def load_default_page(self, search_query=""):
#         self.clear_content()
#         DefaultPage(self.content_frame, search_query=search_query).pack(fill=tk.BOTH, expand=True)

#     # Load function
#     def load_post_admin(self):
#         self.clear_content()
#         PostAdminPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

#     def show_booking_panel(self):
#         self.clear_content()
#         panel = BookingPanel(self.content_frame)
#         panel.pack(fill=tk.BOTH, expand=True)
       


    
# # === APP START ===
# def start_app():

#     create_tables_if_not_exist()
#     ensure_photo_column()
#     splash = SplashScreen()
#     splash.mainloop()

#     app = AdminPanel()
#     app.mainloop()
    

# if __name__ == "__main__":
#     start_app()







import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os, sys
import sqlite3
from student_list import StudentListPanel
from payment_panel import PaymentPanel
from add_student import AddStudentPanel
from shop_rental import ShopRentalPanel
from default_page import DefaultPage 
from post_admin import PostAdminPanel
from ads_booking import BookingPanel

from db_setup import create_tables_if_not_exist, ensure_photo_column, DB_PATH

print("DB Path in main.py:", DB_PATH)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# === SPLASH SCREEN ===
class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loading...")
        self.geometry("600x350")
        self.configure(bg="#f8fffd")
        self.overrideredirect(True)

        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f"600x350+{x}+{y}")

        main_frame = tk.Frame(self, bg="#2F7688", bd=2, relief="groove")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=300)

        try:
            img = Image.open(resource_path("assets/logo2.png"))
            img = img.resize((80, 80))
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(main_frame, image=self.logo_img, bg="#2F7688").pack(pady=(20, 10))
        except:
            tk.Label(main_frame, text="[Logo]", font=("Arial", 16), bg="#2F7688", fg="#5fe0d7").pack(pady=(20, 10))

        tk.Label(main_frame, text="Hostel & Rent Management", font=("Helvetica", 20, "bold"), bg="#2F7688", fg="#080808").pack()

        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start(15)

        tk.Label(main_frame, text="Loading Application....", font=("Arial", 12), bg="#2F7688", fg="#313535").pack()
        self.after(3000, self.close_splash)

    def close_splash(self):
        self.progress.stop()
        self.destroy()


# === ADMIN PANEL ===
class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hostel Name Admin Panel")
        self.geometry("1200x700")
        self.configure(bg="white")

        # --- Sidebar (scrollable) ---
        self.sidebar_outer = tk.Frame(self, bg="#2F7688", width=250)
        self.sidebar_outer.pack(side=tk.LEFT, fill=tk.Y)

        self.sidebar_canvas = tk.Canvas(self.sidebar_outer, bg="#2F7688", width=250, highlightthickness=0)
        self.sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.sidebar_scrollbar = tk.Scrollbar(self.sidebar_outer, orient=tk.VERTICAL, command=self.sidebar_canvas.yview)
        self.sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)

        self.sidebar = tk.Frame(self.sidebar_canvas, bg="#2F7688")
        self.sidebar_canvas.create_window((0,0), window=self.sidebar, anchor="nw")

        def on_frame_configure(event):
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))

        self.sidebar.bind("<Configure>", on_frame_configure)

        # --- Content frame ---
        self.content_frame = tk.Frame(self, bg="#2F7688")
        self.content_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # --- Sidebar Logo ---
        try:
            logo_img = Image.open(resource_path("assets/logo2.png"))
            logo_img = logo_img.resize((120, 120))
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(self.sidebar, image=self.logo, bg="#2F7688").pack(pady=10)
        except:
            tk.Label(self.sidebar, text="[Logo]", font=("Arial", 24, "bold"), bg="#2F7688", fg="white").pack(pady=10)

        # --- Sidebar Buttons ---
        def create_sidebar_btn(text, command):
            return tk.Button(self.sidebar, text=text, font=("Arial", 14), width=20, pady=10, command=command,
                             bg="#2297B4", fg="white", activebackground="#9FA7A9", bd=0, cursor="hand2")

        create_sidebar_btn("🏫 Student List", self.load_student_list).pack(pady=5)
        create_sidebar_btn("💳 Payment", self.load_payment).pack(pady=5)
        create_sidebar_btn("➕ Add Student", self.load_add_student).pack(pady=5)
        create_sidebar_btn("🏬 Flat Rental", self.load_shop_rental).pack(pady=5)
        create_sidebar_btn("🅰️ Post Ads", self.load_post_admin).pack(pady=5)
        create_sidebar_btn("💰 Online Renter", self.show_booking_panel).pack(pady=5)

        # --- Search Frame ---
        search_frame = tk.Frame(self.sidebar, bg="#2F7688")
        search_frame.pack(pady=20, padx=10, fill=tk.X)

        tk.Label(search_frame, text="Search by Name or ID:", font=("Arial", 12), bg="#099f95", fg="white").pack(anchor="w")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 12))
        search_entry.pack(pady=5, fill=tk.X)
        search_entry.bind("<Return>", lambda event: self.perform_search())

        search_btn = tk.Button(search_frame, text="Search", command=self.perform_search, bg="#1abc9c", fg="white")
        search_btn.pack(fill=tk.X)

        refresh_btn = tk.Button(search_frame, text="⟳ Refresh", bg="#3498db", fg="white",
                                font=("Arial", 12, "bold"), command=self.refresh_ui)
        refresh_btn.pack(fill=tk.X, pady=(30,0))

        # Load default page
        self.load_default_page()


    # === CONTENT METHODS ===
    def refresh_ui(self):
        self.clear_content()
        self.load_default_page()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def load_student_list(self):
        self.clear_content()
        StudentListPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def load_payment(self):
        self.clear_content()
        PaymentPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def load_add_student(self):
        self.clear_content()
        AddStudentPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def load_shop_rental(self):
        self.clear_content()
        ShopRentalPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def perform_search(self):
        query = self.search_var.get().strip()
        self.load_default_page(search_query=query)

    def load_default_page(self, search_query=""):
        self.clear_content()
        DefaultPage(self.content_frame, search_query=search_query).pack(fill=tk.BOTH, expand=True)

    def load_post_admin(self):
        self.clear_content()
        PostAdminPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def show_booking_panel(self):
        self.clear_content()
        BookingPanel(self.content_frame).pack(fill=tk.BOTH, expand=True)


# === APP START ===
def start_app():
    create_tables_if_not_exist()
    ensure_photo_column()
    splash = SplashScreen()
    splash.mainloop()

    app = AdminPanel()
    app.mainloop()


if __name__ == "__main__":
    start_app()
