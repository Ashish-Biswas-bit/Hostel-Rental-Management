# Hostel & Rent Management System

A complete solution for managing hostel, flat, and shop rentals with both desktop (Tkinter) and web (Flask) interfaces.

## Features

- **Admin Desktop App (Tkinter):**
  - Student/tenant management
  - Hostel/flat/shop rental management
  - Payment tracking and history
  - Image upload and preview
  - Booking approval and email notifications
- **Web Portal (Flask):**
  - Property listings and search
  - Responsive design (HTML/CSS/JS)
  - Online booking form
  - Contact and newsletter forms
- **Database:**
  - SQLite3 for all data storage
  - Tables for ads, bookings, students, payments, shops, etc.

## Technologies Used

- **Python 3** (Tkinter, Flask, sqlite3, Pillow)
- **HTML5, CSS3, JavaScript** (vanilla JS, Font Awesome)
- **Jinja2** (Flask templates)
- **SMTP** (email notifications)
- **Node.js** (optional, for server.js)

## Getting Started

### 1. Install Requirements
- Python 3.x
- Flask (`pip install flask`)
- Pillow (`pip install pillow`)

### 2. Run the Desktop Admin App
```bash
python main.py
```

### 3. Run the Web Server
```bash
python web_server.py
```
Visit [http://localhost:5000/](http://localhost:5000/) in your browser.

### 4. Database
- The database file is `ads.db` (created automatically).
- Images are stored in `static/uploads/` and `renter_images/`.

## Project Structure
```
├── add_student.py
├── ads_booking.py
├── check_payment_history.py
├── create_tables.py
├── db_setup.py
├── main.py
├── payment_panel.py
├── post_admin.py
├── shop_rental.py
├── student_list.py
├── web_server.py
├── server.js
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
│   └── ads.html
├── database/
│   └── student_images/
└── README.md
```

## Usage
- **Admin:** Use the desktop app for full management.
- **Users:** Browse, search, and book properties via the web portal.

## Accessibility & Best Practices
- Accessible forms and navigation
- Responsive design for mobile and desktop
- Error handling and user feedback

## License
MIT

---
**Developed by Ashish Biswas**
