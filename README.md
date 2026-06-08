# Excellence Global School — Website

A production-ready, AI-powered school website built with **Flask**. Includes a modern public site, online admissions, contact/inquiry system, Gemini AI assistant, and a full admin panel.

---

## Features

### Public Website
- **20+ pages** — Home, About, Vision & Mission, Academics, Facilities, Infrastructure, Gallery, Events, News, Admissions, FAQ, Contact, Careers, AI Assistant, and more
- **Hero banner carousel** — Auto-sliding campus images with manual swipe and arrow navigation
- **Gallery** — 12+ campus images with featured highlights and category filters
- **News & Events** — Articles and upcoming events with images
- **Online admissions** — Application form with photo upload and unique admission ID
- **Contact / inquiries** — Typed queries (Admission, Career, Campus Visit, Feedback, etc.)
- **Responsive design** — Bootstrap 5, GSAP, AOS, Swiper, mobile-first layout

### AI (Google Gemini)
- **Chatbot** — Answers questions about admissions, facilities, timings, and school info
- **Admission Assistant** — Personalized admission guidance by age, class, and location
- **Career Guidance** — Stream-based career advice for students
- **Admin AI Tools** — FAQ generator and notice summarizer
- **Model:** `gemini-2.5-flash` (with automatic fallback if needed)

### Admin Panel (`/admin`)
- Dashboard with stats and recent activity
- **Admissions** — View applications, update status, see full student details
- **Queries** — Contact form submissions with inquiry type, name, email, full message
- **Content management** — Gallery, News, Events, FAQs, Careers, Testimonials
- Role-based access (admin / editor)

### Security & Production
- CSRF protection, rate limiting, input validation
- SQLite database (configurable via `DATABASE_URL`)
- Gunicorn + Nginx deployment guide (`DEPLOYMENT.md`)
- Environment-based configuration (no secrets in code)

---

## Requirements

- **Python 3.10+** (3.12 recommended)
- **pip** (comes with Python)

No virtual environment is required. Install packages globally or use a venv only if you prefer it.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/school-website.git
cd school-website
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env
```

Edit `.env` and set at minimum:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Random secret string for Flask sessions |
| `GEMINI_API_KEY` | Google AI Studio API key ([get one here](https://aistudio.google.com/apikey)) |
| `GEMINI_MODEL` | `gemini-2.5-flash` (recommended) |

Optional: `MAIL_*` settings for email notifications on admissions and contact forms.

### 4. Download images (first time only)

```bash
python scripts/download_images.py
```

### 5. Run the application

```bash
python run.py
```

Open **http://localhost:5000**

### 6. Admin panel

- URL: **http://localhost:5000/admin**
- Default login is created on first run — **change the password immediately** after first login via the admin account settings or database.

---

## Test Gemini AI

```bash
python scripts/test_gemini.py
```

Expected output: `SUCCESS: Working` (or similar one-word reply).

If it fails, verify `GEMINI_API_KEY` in `.env` and that `GEMINI_MODEL=gemini-2.5-flash`.

---

## Project Structure

```
School/
├── app/
│   ├── __init__.py          # App factory, DB seeding
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── models/              # SQLAlchemy models
│   ├── forms/               # WTForms
│   ├── blueprints/          # main, admin, ai routes
│   ├── services/            # Email service
│   ├── ai/                  # Gemini integration
│   ├── utils/               # Helpers
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JS, images, uploads
├── scripts/
│   ├── download_images.py   # Download campus images
│   └── test_gemini.py       # Test AI connection
├── run.py                   # Development server
├── wsgi.py                  # Production entry point
├── requirements.txt
├── .env.example             # Environment template (copy to .env)
└── DEPLOYMENT.md            # Production deployment guide
```

---

## Main Routes

| Page | URL |
|------|-----|
| Home | `/` |
| About | `/about` |
| Gallery | `/gallery` |
| News | `/news` |
| Events | `/events` |
| Admissions | `/admissions` |
| Apply Online | `/apply-online` |
| Contact | `/contact` |
| AI Assistant | `/ai-assistant` |
| Admin | `/admin` |

---

## Push to GitHub

### First-time setup

```bash
cd d:\School

# Ensure secrets and venv are NOT tracked
git rm -r --cached .env venv 2>nul
git rm -r --cached **/__pycache__ 2>nul

# Stage project files (respects .gitignore)
git add .
git status

# Commit
git commit -m "Initial commit: Excellence Global School website"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/school-website.git
git branch -M main
git push -u origin main
```

### Later updates

```bash
git add .
git commit -m "Describe your changes"
git push
```

> **Important:** Never commit `.env` — it contains API keys and passwords. Only commit `.env.example`.

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Required | Default |
|----------|----------|---------|
| `FLASK_ENV` | No | `development` |
| `SECRET_KEY` | Yes (production) | — |
| `GEMINI_API_KEY` | For AI features | — |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` |
| `SCHOOL_NAME` | No | Excellence Global School |
| `DATABASE_URL` | No | SQLite `school.db` |

---

## Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for Gunicorn, Nginx, and Linux server setup.

```bash
pip install -r requirements.txt
python scripts/download_images.py
# Set FLASK_ENV=production and SECRET_KEY in .env
gunicorn -c gunicorn.conf.py wsgi:app
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask 3, SQLAlchemy, Flask-Login, Flask-WTF |
| AI | Google Gemini (`gemini-2.5-flash`) |
| Frontend | Bootstrap 5, GSAP, AOS, Swiper, GLightbox |
| Database | SQLite (default) |
| Email | Flask-Mail (SMTP) |
| Server | Gunicorn + Nginx |

---

## License

This project is for educational and institutional use. Customize school name, branding, and content for your institution.
