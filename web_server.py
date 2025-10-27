from datetime import datetime
from flask import Flask, jsonify, render_template, request
import sqlite3, json


from db_setup import DB_PATH

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, type, title, rent, location, description, image_path FROM ads ORDER BY id DESC")
    ads = cur.fetchall()
    conn.close()

    # Convert to JSON
    ads_json = json.dumps([
        {
            "id": ad[0],
            "type": ad[1],
            "title": ad[2],
            "rent": ad[3],
            "location": ad[4],
            "description": ad[5],
            "image_path": ad[6]
        } for ad in ads
    ])

    return render_template("ads.html", ads_json=ads_json)


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
    
    
if __name__ == "__main__":
    app.run(debug=True)


