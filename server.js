const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");
const bodyParser = require("body-parser");

const app = express();
const PORT = 3000;

// Serve static files
app.use(express.static(path.join(__dirname, "public")));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Connect SQLite DB
const dbPath = path.join(__dirname, "db", "hostel.db");
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) console.error("DB Connection Error:", err);
    else console.log("Connected to SQLite DB");
});

// API to fetch ads
app.get("/api/ads", (req, res) => {
    db.all("SELECT id, type, title, rent, location, description, image_path FROM ads ORDER BY id DESC", [], (err, rows) => {
        if (err) return res.status(500).json({ error: err.message });
        res.json(rows);
    });
});

// API to submit booking
app.post("/api/book", (req, res) => {
    const { ad_id, name, email, phone } = req.body;

    if (!ad_id || !name || !email || !phone) {
        return res.status(400).json({ error: "All fields are required" });
    }

    db.run(
        "CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, ad_id INTEGER, name TEXT, email TEXT, phone TEXT, date TEXT)",
        [],
        (err) => {
            if (err) console.error(err);
        }
    );

    const date = new Date().toISOString();
    db.run(
        "INSERT INTO bookings (ad_id, name, email, phone, date) VALUES (?, ?, ?, ?, ?)",
        [ad_id, name, email, phone, date],
        function(err) {
            if (err) return res.status(500).json({ error: err.message });
            res.json({ success: true, booking_id: this.lastID });
        }
    );
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
