import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db_setup import DB_PATH
from PIL import Image, ImageTk

class BookingPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.build_ui()
        self.load_bookings()

    def build_ui(self):
        tk.Label(self, text="📋 Bookings", font=("Helvetica", 18, "bold")).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("ID", "Renter", "Phone", "Ad Title", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.show_booking_details)

    def load_bookings(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.name, b.phone, a.title, b.status, a.image_path
            FROM bookings b
            JOIN ads a ON b.ad_id = a.id
            ORDER BY b.booking_time DESC
        """)
        self.bookings = cur.fetchall()
        conn.close()
        for b in self.bookings:
            self.tree.insert("", tk.END, values=b[:5])

    def show_booking_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        booking = self.bookings[index]

        top = tk.Toplevel(self)
        top.title("Booking Details")

        tk.Label(top, text=f"Renter: {booking[1]}").pack(pady=5)
        tk.Label(top, text=f"Phone: {booking[2]}").pack(pady=5)
        tk.Label(top, text=f"Ad Title: {booking[3]}").pack(pady=5)
        tk.Label(top, text=f"Status: {booking[4]}").pack(pady=5)

        # Show Image
        try:
            img = Image.open(booking[5])
            img = img.resize((250, 200))
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(top, image=photo)
            img_label.image = photo
            img_label.pack(pady=10)
        except:
            tk.Label(top, text="No image available").pack(pady=10)

        # Accept / Reject Buttons
        btn_frame = tk.Frame(top)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="✅ Accept", command=lambda: self.update_status(booking[0], "Accepted", top)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Reject", command=lambda: self.update_status(booking[0], "Rejected", top)).pack(side=tk.LEFT, padx=5)

    def update_status(self, booking_id, status, window):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", f"Booking {status} successfully!")
        window.destroy()
        self.load_bookings()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Booking Manager")
    root.geometry("700x400")
    BookingPanel(root)
    root.mainloop()
