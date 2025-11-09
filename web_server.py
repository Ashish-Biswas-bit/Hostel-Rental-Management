from datetime import datetime
from flask import Flask, jsonify, render_template, request, url_for
import sqlite3, json, os


from db_setup import DB_PATH

app = Flask(__name__)

@app.route("/")
def index():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # Use SELECT * so missing columns on older DBs won't raise errors
        cur.execute("SELECT * FROM ads ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        def image_url_from_db(path):
            if not path:
                return url_for('static', filename='uploads/edit.jpg')
            if isinstance(path, str) and path.startswith('/'):
                return path
            base = os.path.basename(path)
            return url_for('static', filename=f'uploads/{base}')

        ads = []
        for r in rows:
            # Use safe access for optional columns
            keys = r.keys()
            def g(k):
                return r[k] if k in keys else None

            ad = {
                "id": g('id'),
                "type": (g('type') or ''),
                "category": (g('category') or ''),
                "gender": (g('gender') or ''),
                "title": (g('title') or ''),
                "rent": (g('rent') or ''),
                "location": (g('location') or ''),
                "description": (g('description') or ''),
                "image_path": image_url_from_db(g('image_path')),
                "phone": (g('phone') or ''),
                "email": (g('email') or ''),
                "whatsapp": (g('whatsapp') or '')
            }
            ads.append(ad)

        return render_template("ads.html", ads=ads)

    except Exception as e:
        # Log the exception to console for debugging and return an empty list to avoid 500
        import traceback
        print("Error in / route:", e)
        traceback.print_exc()
        return render_template("ads.html", ads=[])


@app.route("/book_ad", methods=["POST"])
def book_ad():
    try:
        data = request.get_json()
        ad_id = data.get("ad_id")
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not ad_id or not name or not email or not phone:
            return jsonify({"success": False, "error": "Missing required fields"})

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookings (ad_id, name, email, phone, booking_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ad_id, name, email, phone, booking_date, "Pending"))
        conn.commit()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        print("Booking error:", e)
        return jsonify({"success": False, "error": str(e)})
    

@app.route('/api/ads', methods=['GET'])
def api_ads():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM ads ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        def image_url_from_db(path):
            if not path:
                return url_for('static', filename='uploads/edit.jpg')
            if isinstance(path, str) and path.startswith('/'):
                return path
            base = os.path.basename(path)
            return url_for('static', filename=f'uploads/{base}')

        ads = []
        for r in rows:
            keys = r.keys()
            def g(k):
                return r[k] if k in keys else None

            ad = {
                "id": g('id'),
                "type": (g('type') or ''),
                "category": (g('category') or ''),
                "gender": (g('gender') or ''),
                "title": (g('title') or ''),
                "rent": (g('rent') or ''),
                "location": (g('location') or ''),
                "description": (g('description') or ''),
                "image_path": image_url_from_db(g('image_path')),
                "phone": (g('phone') or ''),
                "email": (g('email') or ''),
                "whatsapp": (g('whatsapp') or '')
            }
            ads.append(ad)

        return jsonify(ads)
    except Exception as e:
        print('Error in /api/ads:', e)
        return jsonify([])
    
    
if __name__ == "__main__":
    app.run(debug=True)


