# Deploy on Render

## Fix for `eventlet` / Python 3.14 crash

Render was failing because:
1. **Start command** used `gunicorn run:app` (dev entry point)
2. **Socket.IO** tried to load `eventlet`, which breaks on Python 3.12+

This project now uses **`threading`** for Socket.IO and **`wsgi:app`** for production.

---

## Render Dashboard Settings

| Setting | Value |
|---------|--------|
| **Runtime** | Python 3 |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `gunicorn wsgi:app --config gunicorn.conf.py` |
| **Python Version** | Set env `PYTHON_VERSION` = `3.12.8` (or use `runtime.txt`) |

> **Important:** Change Start Command from `gunicorn run:app` to the command above.

---

## Required Environment Variables

Set these in Render → Environment:

```
FLASK_ENV=production
SECRET_KEY=<long-random-string>
JWT_SECRET_KEY=<long-random-string>
SOCKETIO_ASYNC_MODE=threading
```

Optional (recommended for production):

```
DATABASE_URL=<from Render PostgreSQL>
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
SCHOOL_NAME=Blue Bells Public School
SCHOOL_EMAIL=...
MAIL_USERNAME=...
MAIL_PASSWORD=...
```

---

## Database on Render

SQLite **does not persist** on Render (files are wiped on redeploy).

1. Create a **PostgreSQL** database in Render
2. Link it to your web service (sets `DATABASE_URL` automatically)
3. Redeploy

---

## Deploy with Blueprint (optional)

If using `render.yaml` from the repo root, Render will use the correct start command automatically.

---

## Local vs Production

| Command | Use |
|---------|-----|
| `python run.py` | Local development |
| `gunicorn wsgi:app --config gunicorn.conf.py` | Production (Render) |
