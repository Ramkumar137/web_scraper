# Cookit Scraper Pipeline

## Description
Cookit Scraper is an automated backend system that collects recipes from cooking websites using sitemap URLs.  
It extracts recipe links, queues them, scrapes structured recipe data in the background, and stores the results in a database.  
Once started, the system runs automatically without manual effort.

---

## What This Project Does
- Accepts a recipe sitemap URL via API
- Extracts all recipe links from the sitemap
- Stores links in a PostgreSQL FIFO queue
- Background worker scrapes recipe details
- Saves structured recipe data into MongoDB
- Uses polite delays to avoid IP bans

---

## Architecture
    Client
    ↓
    FastAPI (Upload Sitemap)
    ↓
    PostgreSQL (URL Queue)
    ↓
    Background Worker (Scraper)
    ↓
    MongoDB (Recipe Data)


---

## Project Structure

    cookit-scraper/
    │
    ├── api/
    │ └── main.py
    ├── worker/
    │ └── scraper.py
    ├── db/
    │ ├── postgres.py
    │ └── mongo.py
    ├── utils/
    │ ├── delay.py
    │ └── mailer.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md


---

## How to Run Locally

### 1. Install dependencies
pip install -r requirements.txt

### 2. Set environment variables

DATABASE_URL=postgresql://username:password@localhost:5432/cookit

MONGO_URI=mongodb+srv://username:password@cluster/cookit

EMAIL_USER= your_email_id

EMAIL_PASS=gmail_password

### 4. Run API service
uvicorn api.main:app --reload

### 5. Run background worker (new terminal)
python worker/scraper.py

### 6. Upload sitemap

    Open:
    
    http://127.0.0.1:8000/docs
    
    Use POST /upload-sitemap with:
    
    {
      "sitemap_url": "https://www.bbcgoodfood.com/sitemaps/2025-Q1-recipe.xml"
    }

## How to Deploy (Render – Free Tier)
### 1. Push code to GitHub
git push origin main

### 2. Create PostgreSQL on Render

Render → New → PostgreSQL (Free)

Copy Internal Database URL

Set it as DATABASE_URL

Table auto-creates on startup

### 3. Deploy FastAPI (Web Service)

Start Command

uvicorn api.main:app --host 0.0.0.0 --port 10000


Environment Variables

DATABASE_URL
MONGO_URI
EMAIL_USER
EMAIL_PASS

### 4. Deploy Background Worker

Start Command

python worker/scraper.py

Same environment variables as API

### 5. Cloud Test

Call:

POST https://<your-service>.onrender.com/upload-sitemap

URLs will be queued, scraped, and stored automatically.
