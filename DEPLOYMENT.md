# Deployment Guide for Hostel Rental Management

This guide covers deploying your Flask web application to **Render** or **Railway**.

## Prerequisites

- GitHub account with your repository pushed
- Render or Railway account (both free to sign up)
- Python 3.11+

---

## **Option 1: Deploy to Render** ✅ Recommended

### Step 1: Connect Your Repository
1. Go to [render.com](https://render.com)
2. Sign up or log in with your GitHub account
3. Click **"New +"** → **"Web Service"**
4. Select your `Hostel-Rental-Management` repository
5. Click **"Connect"**

### Step 2: Configure Deployment
- **Name**: `hostel-rental-app` (or your choice)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT web_server:app`

### Step 3: Environment Variables
Click **"Advanced"** and add:
```
FLASK_ENV = production
PYTHON_VERSION = 3.11
```

### Step 4: Add Persistent Storage (for database)
1. Scroll to **"Disks"**
2. Click **"Add Disk"**
3. **Name**: `hostel_data`
4. **Mount Path**: `/data`
5. **Size**: `1 GB`

### Step 5: Deploy
- Click **"Deploy"**
- Wait 3-5 minutes
- Your app will be live at: `https://hostel-rental-app.onrender.com`

---

## **Option 2: Deploy to Railway**

### Step 1: Install Railway CLI (Optional but Recommended)
```bash
npm install -g @railway/cli
```

### Step 2: Connect Repository
1. Go to [railway.app](https://railway.app)
2. Sign up or log in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Authorize Railway to access GitHub

### Step 3: Configure Environment
1. Railway will auto-detect `Dockerfile` and `railway.toml`
2. Add environment variables:
   - Click **"Add Variable"**
   - `FLASK_ENV`: `production`

### Step 4: Deploy
- Railway will automatically build and deploy
- Your app will be live at: `https://your-project-name.up.railway.app`

---

## **Deployment Comparison**

| Feature | Render | Railway |
|---------|--------|---------|
| **Free Tier** | Yes (with 15 min inactivity spindown) | Yes (limited) |
| **Persistent Storage** | Yes (Disks) | Yes (Volumes) |
| **Database Support** | PostgreSQL available | PostgreSQL available |
| **Build Time** | ~2-3 min | ~1-2 min |
| **Ease of Use** | Easy (Web UI) | Easy (Web UI) |
| **Custom Domain** | Yes | Yes |

---

## **Post-Deployment Setup**

### 1. Test Your Deployment
```bash
curl https://your-app-url.com/
curl https://your-app-url.com/api/ads
```

### 2. Add Sample Data
You need to add property ads to your database. For now, the `/api/ads` endpoint will return empty.

#### Option A: Via Admin Desktop App
1. Run the admin app locally (for testing)
2. Connect to the same database (see below)

#### Option B: Create a Simple Admin Endpoint
Create `admin_routes.py` and import it in `web_server.py` to add CRUD operations:

```python
@app.route('/admin/add-ad', methods=['POST'])
def add_ad():
    # Validation needed before production
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ads (type, category, gender, title, rent, location, description, phone, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data['type'], data['category'], data['gender'], data['title'], 
          data['rent'], data['location'], data['description'], data['phone'], data['email']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})
```

---

## **Database Persistence**

### SQLite (Current Setup - Local)
- Database stored at `/data/ads.db` on the server
- Persists with Render Disks or Railway Volumes
- **Limitation**: Single-server only, no scalability

### PostgreSQL (Recommended for Production)
1. **Render**: Add PostgreSQL database from Render dashboard
2. **Railway**: Add PostgreSQL template
3. Update `requirements.txt`:
   ```
   psycopg2-binary==2.9.6
   ```
4. Modify `web_server.py` to use PostgreSQL instead of SQLite

**PostgreSQL connection example**:
```python
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')
url = urlparse(DATABASE_URL)
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
```

---

## **Troubleshooting**

### App crashes immediately
- Check logs: `Logs` tab in Render/Railway dashboard
- Common issues:
  - Missing `requirements.txt`
  - Wrong start command
  - Import errors in `web_server.py`

### Database connection fails
- Ensure `/data` directory exists or use PostgreSQL
- Check file permissions: `chmod 777 /data`

### Static files not loading
- Ensure `static/` folder exists with CSS/JS files
- Flask will serve from `static/` by default

### Port issues
- Use `$PORT` environment variable (already set up in Procfile)
- Don't hardcode port to 5000 or 8000

---

## **Custom Domain (Optional)**

### Render
1. Go to **"Settings"** → **"Custom Domain"**
2. Add your domain (e.g., `hostel.example.com`)
3. Follow DNS instructions

### Railway
1. Go to **"Settings"** → **"Custom Domain"**
2. Add domain and point DNS records

---

## **Next Steps**

1. ✅ Deploy to Render or Railway
2. ✅ Test the web portal
3. ⚠️ Add authentication for admin functions
4. 🔄 Set up PostgreSQL for scalability
5. 📧 Configure email notifications
6. 🔒 Add HTTPS (auto-enabled on both platforms)

---

## **Support**

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Flask Docs**: https://flask.palletsprojects.com

For issues, check the deployment logs first!
