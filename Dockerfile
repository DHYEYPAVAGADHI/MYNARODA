# ============================================================
# GREEN NARODA • CLEAN NARODA — Application Image
# ============================================================
# A single image used by the web, worker, and beat services
# (see docker-compose.yml). Python 3.12 matches the versions
# the project's pinned dependencies are tested against.
# ============================================================

FROM python:3.12-slim

# ─── Environment ──────────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ─── System dependencies ──────────────────────────────────────────────────────
# gcc/libpq-dev: build psycopg2 if a wheel is unavailable
# gettext: compile translation (.po -> .mo) files
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─── Python dependencies (cached layer) ───────────────────────────────────────
COPY requirements/ requirements/
# Build with production requirements by default; override at build time with
#   --build-arg REQUIREMENTS=requirements/development.txt
ARG REQUIREMENTS=requirements/production.txt
RUN pip install --upgrade pip && pip install -r ${REQUIREMENTS}

# ─── Application code ─────────────────────────────────────────────────────────
COPY . .

EXPOSE 8000

# Default command (overridden per-service in docker-compose.yml).
# For production, run migrations + collectstatic + gunicorn — see README.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
