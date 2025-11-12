import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db_setup import DB_PATH
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        # Select all columns, handle missing ones
        cur.execute("""
            SELECT b.id, b.name, b.phone, a.title, b.status, a.image_path, a.location, b.email
            FROM bookings b
            JOIN ads a ON b.ad_id = a.id
            ORDER BY b.booking_date DESC
        """)
        self.bookings = cur.fetchall()
        conn.close()
        for b in self.bookings:
            # If location or email missing, fill with empty string
            vals = list(b[:5])
            if len(b) < 8:
                vals += ["", ""]
            self.tree.insert("", tk.END, values=vals)

    def show_booking_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        booking = self.bookings[index]

        top = tk.Toplevel(self)
        top.title("Booking Details")

        tk.Label(top, text=f"Renter: {booking[1]}" if booking[1] else "Renter: N/A").pack(pady=5)
        tk.Label(top, text=f"Phone: {booking[2]}" if booking[2] else "Phone: N/A").pack(pady=5)
        tk.Label(top, text=f"Email: {booking[7]}" if len(booking) > 7 and booking[7] else "Email: N/A").pack(pady=5)
        tk.Label(top, text=f"Ad Title: {booking[3]}" if booking[3] else "Ad Title: N/A").pack(pady=5)
        tk.Label(top, text=f"Location: {booking[6]}" if len(booking) > 6 and booking[6] else "Location: N/A").pack(pady=5)
        tk.Label(top, text=f"Status: {booking[4]}" if booking[4] else "Status: N/A").pack(pady=5)

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

        tk.Button(btn_frame, text="✅ Accept", command=lambda: self.handle_decision(booking, "Accepted", top)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Reject", command=lambda: self.handle_decision(booking, "Rejected", top)).pack(side=tk.LEFT, padx=5)

    def handle_decision(self, booking, status, window):
        self.update_status(booking[0], status, window)
        # Send email notification (placeholder)
        self.send_email_notification(booking[7], status, booking)

    def send_email_notification(self, email, status, booking):
        # Real email sending via SMTP (configure below)
        sender_email = "20232056010@nwu.ac.bd"  # Replace with your email
        sender_password = "wvvr zuko dcor odcw"        # Replace with your password
        smtp_server = "smtp.gmail.com"           # Change if not using Gmail
        smtp_port = 587

        renter_name = booking[1] if booking[1] else "Valued Guest"
        property_title = booking[3] if booking[3] else "Your Property"
        location = booking[6] if len(booking) > 6 and booking[6] else "the specified location"
        
        subject = f"🏠 Your Booking Has Been {status} - HomeFinder"
        
        if status == "Accepted":
            body = f"""Dear {renter_name},

🎉 Great News! Your booking has been ACCEPTED!

Property Details:
📍 Title: {property_title}
📌 Location: {location}

Your booking is confirmed. The property owner will contact you shortly with further details, payment information, and next steps.

Important Information:
✓ Please ensure you have reviewed all property amenities and terms
✓ Keep this email for your records
✓ The owner will reach out within 24 hours

If you have any questions, feel free to contact us or reply to this email.

Best Regards,
HomeFinder Team
📧 hostel2rent@homefinder.com
📞 +880 17445-02112
🏢 34 B Sonadanga, Khulna

---
This is an automated message. Please do not reply directly to this email."""
        
        else:  # Rejected
            body = f"""Dear {renter_name},

Thank you for your interest in {property_title} at {location}.

Unfortunately, your booking request has been REJECTED. This may be due to:
- Property already booked
- Unavailability on requested dates
- Other requirements not met

We recommend:
✓ Browsing other similar properties on our platform
✓ Adjusting your requirements
✓ Contacting the owner directly with questions

We have many other excellent properties available. Please visit our website to explore more options.

HomeFinder Team
📧 hostel2rent@homefinder.com
📞 +880 17445-02112
🏢 34 B Sonadanga, Khulna

---
This is an automated message. Please do not reply directly to this email."""

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()
            messagebox.showinfo("✅ Email Sent", f"A confirmation email has been sent to {email}.\nStatus: {status}")
        except Exception as e:
            messagebox.showerror("📧 Email Error", f"Failed to send email to {email}:\n{str(e)}")

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
