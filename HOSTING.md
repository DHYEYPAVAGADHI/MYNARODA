# Hosting Guide — Green Naroda • Clean Naroda

This is a standalone, practical guide to getting this Django site live on the internet.
It covers three paths, easiest first. Pick one — you don't need to read all three.

| Path | Best for | Effort |
|------|----------|--------|
| [A. Managed platform (Railway / Render)](#a-managed-platform-railway--render-easiest) | No server experience, fastest to launch | Low |
| [B. Docker on your own VPS](#b-docker-on-your-own-vps) | Full control, already comfortable with Docker | Medium |
| [C. Manual VPS (Gunicorn + Nginx)](#c-manual-vps-gunicorn--nginx) | Full control, no Docker | High |

Before any of these, read **[Before You Deploy](#before-you-deploy)** — it applies to all three.

---

## Before You Deploy

### 1. Environment variables
Copy `.env.example` to `.env` and fill in real values. The ones that matter most for a live site:

| Variable | Set to |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DEBUG` | `False` |
| `SECRET_KEY` | A freshly generated key — see below, never reuse the dev one |
| `ALLOWED_HOSTS` | Your real domain(s), comma-separated |
| `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.com,https://www.yourdomain.com` |
| `DB_*` | Your production PostgreSQL credentials |

Generate a strong secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Database — use PostgreSQL, not the SQLite file
`db.sqlite3` is fine for local testing only. It was intentionally **not included** in the
project zip. For a live site, provision a real PostgreSQL database (every option below
gives you one) and point `DB_*` at it.

### 3. Uploaded photos need persistent storage (Cloudinary)
The Gallery and Student Portal let people upload photos. Platforms like Railway/Render
wipe the local filesystem on every redeploy — anything saved to disk is lost. Set the
`CLOUDINARY_*` variables in `.env` (free tier at [cloudinary.com](https://cloudinary.com))
so uploads persist. Skip this only if you're self-hosting on a VPS with a real disk (Options B/C).

### 4. Multi-language support
This site ships English/Gujarati/Hindi. After any content or template change, recompile
translations before deploying:
```bash
python manage.py compilemessages
```

### 5. The first-deploy checklist
Whichever path you choose, these four commands need to run once against your live database:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py compilemessages
```

---

## A. Managed Platform (Railway / Render) — Easiest

No server to manage, no Nginx to configure. You push code, the platform builds and runs it.
Steps below use **Railway**; **Render** is nearly identical (both auto-detect Django).

1. **Push the project to a GitHub repo** (Railway/Render deploy from Git, not a zip upload).
2. **Create a new project** on [railway.app](https://railway.app) → "Deploy from GitHub repo".
3. **Add a PostgreSQL database** from Railway's plugin marketplace — it auto-injects
   `DATABASE_URL`. If your `config/settings/production.py` reads individual `DB_*` vars
   instead, set them manually from the Postgres plugin's connection details.
4. **Set environment variables** (Railway → Variables tab) — everything from
   [Before You Deploy → Environment variables](#1-environment-variables), plus the
   `CLOUDINARY_*` values (required here — see point 3 above).
5. **Set the start command**:
   ```
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   ```
6. **Set the build/release command** (runs once per deploy) so migrations and static files
   stay current:
   ```
   python manage.py migrate && python manage.py collectstatic --noinput
   ```
7. **Deploy.** Railway gives you a `*.up.railway.app` URL immediately; add your own domain
   under Settings → Domains (free SSL is automatic).
8. Create your admin user once, from Railway's shell/console tab:
   ```
   python manage.py createsuperuser
   ```

> Background tasks (Celery) are optional at launch — the site works without them. If you
> later need them, add a Redis plugin and a second Railway service running
> `celery -A config worker --loglevel=info`.

---

## B. Docker on Your Own VPS

Uses the `Dockerfile` and `docker-compose.yml` already in the project — this starts
PostgreSQL, Redis, the web server, and Celery worker/beat together.

```bash
# 1. On your server, get the code onto it (scp the zip, or git clone)
cd /var/www/green-naroda

# 2. Set production values in .env (see "Before You Deploy" above)
cp .env.example .env
nano .env
#   Also change the default `postgres`/`postgres` DB password in docker-compose.yml
#   before going live — it's a dev default.

# 3. Build and start everything
docker compose up -d --build

# 4. First-time setup (run once)
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py compilemessages
```

The app is now listening on port 8000 inside the server. Put **Nginx** or **Caddy** in
front to handle HTTPS on 80/443 and reverse-proxy to `localhost:8000`. Minimal Nginx example:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then get a free certificate with Certbot: `sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com`

---

## C. Manual VPS (Gunicorn + Nginx)

No Docker — installs everything directly on an Ubuntu server.

```bash
# 1. System packages
sudo apt update && sudo apt install python3.12 python3.12-venv postgresql redis nginx

# 2. Code + virtual environment
cd /var/www/green-naroda
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements/production.txt

# 3. Environment (see "Before You Deploy" above)
cp .env.example .env
nano .env

# 4. First-time setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py compilemessages
python manage.py createsuperuser

# 5. Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Wrap Gunicorn (and Celery, if you use it) in **systemd** services so they restart on
crash/reboot, and put **Nginx** in front the same way as shown in Option B, with Certbot
for HTTPS.

---

## Go-Live Checklist

- [ ] `DEBUG=False`
- [ ] Fresh, unique `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` set to your real domain
- [ ] Real PostgreSQL database, strong password
- [ ] `CLOUDINARY_*` set (unless self-hosting with persistent disk)
- [ ] HTTPS working (padlock in browser)
- [ ] `migrate`, `collectstatic`, `compilemessages` all run against production
- [ ] Admin user created, and you can log into `/admin/`
- [ ] `.env` is **not** committed to any Git repo
- [ ] Test the pledge form, gallery upload, and student portal end to end on the live URL
