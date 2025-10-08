import sqlite3
import os



def get_persistent_db_path():
    app_dir = os.path.join(os.path.expanduser("~"), "Hostel Management")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "hostel.db")

DB_PATH = get_persistent_db_path()

def create_tables_if_not_exist():
    print("Creating tables...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY, name TEXT, building TEXT, room TEXT, photo TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS addresses (
            student_id TEXT PRIMARY KEY, district TEXT, upazila TEXT, union_name TEXT,
            village TEXT, father_name TEXT, guardian_number TEXT, personal_number TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS admission_fee (
            student_id TEXT PRIMARY KEY, amount REAL, date TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id))""")

        # ✅ Missing Tables
    c.execute("""CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            deposit REAL,
            due REAL,
            fine REAL,
            advance REAL,
            date TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )""")

    c.execute("""CREATE TABLE IF NOT EXISTS student_balance (
            student_id TEXT PRIMARY KEY,
            deposit REAL DEFAULT 0,
            due REAL DEFAULT 0,
            fine REAL DEFAULT 0,
            advance REAL DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )""")

    c.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                shop_no TEXT PRIMARY KEY,
                renter_name TEXT,
                phone TEXT,
                address TEXT,
                advance_balance REAL DEFAULT 0,
                monthly_rent REAL DEFAULT 0
            )
        """)
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

    print("Tables created or already exist.")


def ensure_photo_column():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("PRAGMA table_info(students)")
        columns = [col[1] for col in c.fetchall()]
        print("Current columns in students:", columns)  # Debug line
        if "photo" not in columns:
            c.execute("ALTER TABLE students ADD COLUMN photo TEXT")
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Error adding 'photo' column: {e}")

