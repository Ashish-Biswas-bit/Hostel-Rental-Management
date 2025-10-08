import sqlite3
import os

def get_persistent_db_path():
    app_dir = os.path.join(os.path.expanduser("~"), "Hostel Management")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "hostel.db")

DB_PATH = get_persistent_db_path()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Existing Tables
cursor.execute("""CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY, name TEXT, building TEXT, room TEXT, photo TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS addresses (
    student_id TEXT PRIMARY KEY, district TEXT, upazila TEXT, union_name TEXT,
    village TEXT, father_name TEXT, guardian_number TEXT, personal_number TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id))""")

cursor.execute("""CREATE TABLE IF NOT EXISTS admission_fee (
    student_id TEXT PRIMARY KEY, amount REAL, date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id))""")

# ✅ Missing Tables
cursor.execute("""CREATE TABLE IF NOT EXISTS payment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    deposit REAL,
    due REAL,
    fine REAL,
    advance REAL,
    date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS student_balance (
    student_id TEXT PRIMARY KEY,
    total_deposit REAL DEFAULT 0,
    total_due REAL DEFAULT 0,
    total_fine REAL DEFAULT 0,
    total_advance REAL DEFAULT 0,
    FOREIGN KEY(student_id) REFERENCES students(id)
)""")

conn.commit()
conn.close()

print("✅ All required tables have been created!")
