import sqlite3
from db_setup import DB_PATH

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_history'")
    if not c.fetchone():
        print('Table payment_history does NOT exist in DB:', DB_PATH)
    else:
        c.execute('SELECT COUNT(*) FROM payment_history')
        cnt = c.fetchone()[0]
        print('payment_history row count:', cnt)
        if cnt > 0:
            c.execute('SELECT id, student_id, deposit, due, fine, advance, date FROM payment_history LIMIT 50')
            for r in c.fetchall():
                print(r)
except Exception as e:
    print('ERROR:', e)
finally:
    conn.close()
