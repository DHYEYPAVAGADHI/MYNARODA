# 🌳 Green Naroda • Clean Naroda

A civic-campaign web platform for **Naroda, Ahmedabad** — organising a drive to plant
**28,855 trees** and run cleanliness initiatives across all 14 wards, in celebration of
India's 80th Independence Year.

Built with **Django 5.1**. Multi-language (English / Gujarati / Hindi), with a public
campaign site, volunteer & organisation registration, auto-generated certificates,
a photo gallery, events, news, a student corner, and a full admin panel.

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Tech Stack](#-tech-stack)
3. [Project Structure](#-project-structure)
4. [Quick Start (Local Development)](#-quick-start-local-development)
5. [Environment Variables](#-environment-variables)
6. [Common Commands](#-common-commands)
7. [Hosting / Deployment](#-hosting--deployment)
8. [Security Notes](#-security-notes)

---

## ✨ Features

| Area | Description |
|------|-------------|
| **Landing site** | Campaign home page with live progress, mission, gallery, news, events, contact |
| **Pledge / Volunteers** | Citizens take the pledge and register; certificates are generated automatically |
| **Organisations** | Schools, societies, NGOs register via the Competition menu |
| **Gallery** | Community photo uploads (images / media) with categories |
| **Events & News** | Upcoming drives and press updates |
| **Student Corner** | Essay, drawing and quiz competitions |
| **Certificates** | PDF + QR certificate generation and public verification |
| **Admin Panel** | Django Unfold admin, custom dashboard, leadership photo management, backup tools |
| **Multi-language** | English, Gujarati, Hindi (via `django-modeltranslation`) |

---

## 🛠 Tech Stack

- **Backend:** Django 5.1, Django REST Framework
- **Database:** PostgreSQL (production) / SQLite (zero-config local dev)
- **Cache & Queue:** Redis + Celery (worker + beat)
- **Auth:** django-allauth (email + Google OAuth), django-axes (brute-force protection)
- **Media:** Cloudinary (optional) / local filesystem
- **PDF / QR:** reportlab + qrcode
- **Static files:** WhiteNoise
- **Admin UI:** django-unfold

---

## 📁 Project Structure

```
Green-Naroda/
├── manage.py                 # Django entry point
├── Dockerfile                # Container image (web / worker / beat)
├── docker-compose.yml        # Local full-stack (db, redis, web, worker, beat)
├── Makefile                  # Handy commands — run `make help`
├── .env.example              # Copy to .env and fill in values
│
├── config/                   # Project configuration
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── development.py    # Local dev (DEBUG, SQLite, console email)
│   │   └── production.py     # Live (hardened: SSL, HSTS, secure cookies)
│   ├── urls.py               # Root URL router
│   ├── celery.py             # Celery app
│   ├── wsgi.py / asgi.py     # Server entry points
│
├── apps/                     # Application modules
│   ├── accounts/             # Users, auth, OTP
│   ├── volunteers/           # Pledge & volunteer registration
│   ├── competitions/         # Organisation registration + certificates
│   ├── certificates/         # Certificate generation & verification
│   ├── cms/                  # Landing page & content pages
│   ├── gallery/  events/  news/  trees/
│   ├── student_portal/  notifications/  admin_panel/
│
├── core/                     # Shared utilities, middleware, validators
├── templates/                # HTML templates
├── static/                   # CSS, JS, images
├── locale/                   # Translation files (en / gu / hi)
├── scripts/                  # Seed & data helper scripts (run manually)
├── requirements/             # base.txt / development.txt / production.txt
└── dev_archive/              # Old one-off build scripts (kept for history — safe to delete)
```

---

## 🚀 Quick Start (Local Development)

Runs with **zero external services** — uses SQLite, console email, and in-memory Celery.

### Requirements
- Python **3.12** (recommended; 3.11–3.13 also work)

### Steps

```bash
# 1. Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

# 2. Install development dependencies
pip install -r requirements/development.txt

# 3. Create your environment file
cp .env.example .env                 # the defaults work for local dev as-is

# 4. Set up the database
python manage.py migrate

# 5. Create an admin user
python manage.py createsuperuser

# 6. Run the server
python manage.py runserver
```

Open **http://127.0.0.1:8000** — the site is live.
Admin panel: **http://127.0.0.1:8000/admin/**

> 💡 There is also a `Makefile`: `make setup` does steps 2–5 in one command,
> then `make dev` runs the server. Run `make help` to see everything.

---

## 🔑 Environment Variables

Copy `.env.example` → `.env` and fill in real values. Key ones:

| Variable | Purpose | Local dev |
|----------|---------|-----------|
| `SECRET_KEY` | Django secret | a dev default is used automatically |
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` or `...production` | development |
| `DEBUG` | `True` / `False` | `True` |
| `ALLOWED_HOSTS` | comma-separated hostnames | `localhost,127.0.0.1` |
| `DB_*` | PostgreSQL connection (production) | not needed — SQLite is used |
| `REDIS_URL` | Redis for Celery (production) | not needed |
| `EMAIL_*` | SMTP settings | not needed — email prints to console |
| `CLOUDINARY_*` | media hosting (optional) | not needed |
| `GOOGLE_CLIENT_ID` / `SECRET` | Google login (optional) | not needed |
| `SENTRY_DSN` | error monitoring (optional) | leave blank |

> ⚠️ **Never commit your `.env` file.** It is already in `.gitignore`.
> Generate a strong secret key:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🧰 Common Commands

| Command | What it does |
|---------|--------------|
| `python manage.py runserver` | Start the dev server |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py createsuperuser` | Create an admin account |
| `python manage.py collectstatic` | Gather static files (for production) |
| `python manage.py compilemessages` | Compile translations (.po → .mo) |
| `make test` | Run tests with coverage |
| `make lint` / `make format` | Lint / auto-format code |

---

## 🌐 Hosting / Deployment

You have two options. **Option A (Docker)** is the easiest and most reliable.

### Option A — Docker Compose (recommended)

This starts everything: PostgreSQL, Redis, the web server, and Celery worker + beat.

```bash
# 1. Create your environment file and set real production values
cp .env.example .env
#    In .env, set at minimum:
#      DJANGO_SETTINGS_MODULE=config.settings.production
#      DEBUG=False
#      SECRET_KEY=<a strong generated key>
#      ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
#      DB_NAME / DB_USER / DB_PASSWORD  (any values — used by the db container)
#      EMAIL_* and CLOUDINARY_* if you use them

# 2. Build and start all services
docker compose up -d --build

# 3. Run migrations and create an admin user (first time only)
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
```

The site is now on **http://your-server:8000**. Put **Nginx** (or Caddy) in front as a
reverse proxy to handle HTTPS on ports 80/443 and forward to port 8000.

### Option B — Manual server (VPS: Ubuntu, etc.)

```bash
# 1. Install system packages
sudo apt update && sudo apt install python3.12 python3.12-venv postgresql redis nginx

# 2. Get the code and create a virtual environment
cd /var/www/green-naroda
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements/production.txt

# 3. Configure environment
cp .env.example .env    # set production values (see Option A step 1)

# 4. Prepare the app
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 5. Run with Gunicorn (behind Nginx)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

# 6. Run Celery (in separate processes / systemd services)
celery -A config worker --loglevel=info
celery -A config beat  --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Use **systemd** services to keep Gunicorn and Celery running, and **Nginx** as the
HTTPS reverse proxy (with a free certificate from Let's Encrypt / Certbot).

### Production checklist ✅

- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] `DEBUG=False`
- [ ] Strong, unique `SECRET_KEY` (never the dev default)
- [ ] `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` set to your real domain
- [ ] Real PostgreSQL database with a strong password
- [ ] HTTPS enabled (Nginx/Caddy + Let's Encrypt)
- [ ] `collectstatic` run
- [ ] SMTP email credentials set (for real emails)
- [ ] `.env` **not** committed to version control

---

## 🔒 Security Notes

The following were fixed in this cleaned-up version:

1. **Mock Google login is now development-only.** The `/accounts/google/login/`
   mock (which logs in as any email without a password) is registered **only when
   `DEBUG=True`**, so it can never be exposed in production. See `config/urls.py`.
2. **No real credentials in `.env.example`.** Email placeholders replaced with dummy
   values. **If you used the old file, change (rotate) that email password.**
3. **Complete requirements.** All packages the code imports are now listed in
   `requirements/base.txt`, so a fresh install runs without missing-module errors.

Before going live, also confirm the **production checklist** above.

---

*Made for a greener, cleaner Naroda. 🌱*
