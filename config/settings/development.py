
"""
Development Settings
====================
Overrides for local development only.
Debug mode ON, SQLite fallback, console email backend.
"""

from decouple import config  # explicit import — resolves pyflakes star-import warning

from .base import *  # noqa: F401, F403

# ─── Debug ────────────────────────────────────────────────────────────────────

DEBUG = True

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-dev-key-change-in-production-please-do-not-deploy",
)

ALLOWED_HOSTS = ["*"]


# ─── Database — SQLite for zero-config local dev ──────────────────────────────
# Switch to PostgreSQL by setting USE_POSTGRES=True in .env

import os  # noqa: E402

_use_postgres = os.environ.get("USE_POSTGRES", "").lower() in ("1", "true", "yes")

if _use_postgres:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME", default="mynaroda_dev"),
            "USER": config("DB_USER", default="postgres"),
            "PASSWORD": config("DB_PASSWORD", default="postgres"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
            "CONN_MAX_AGE": 0,
        }
    }
else:
    # Zero-config SQLite for local dev without PostgreSQL installed
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }


# ─── Email ────────────────────────────────────────────────────────────────────
# By default, use SMTP if configured, otherwise fallback to console.
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# ── Disable mandatory email verification in dev ─────────────────────────────
# Users registered on localhost are immediately active — no real SMTP needed.
ACCOUNT_EMAIL_VERIFICATION = "none"

# Bypass SSL certificate verification for macOS local development
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    ssl.create_default_context = _create_unverified_https_context


# ─── Cache ────────────────────────────────────────────────────────────────────

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# ─── Session & CSRF (relaxed for dev) ────────────────────────────────────────

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# ─── CORS (open for local dev) ────────────────────────────────────────────────

CORS_ALLOW_ALL_ORIGINS = True


# ─── Static / Media (local filesystem) ───────────────────────────────────────

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


# ─── Celery (in-memory for dev — no Redis needed) ────────────────────────────

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# ─── Debug Toolbar & Extensions ────────────────────────────────────────────────────────────

try:
    import debug_toolbar
    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE = [  # noqa: F405
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: False,
    }
except ImportError:
    pass

try:
    import django_extensions
    INSTALLED_APPS += ["django_extensions"]  # noqa: F405
except ImportError:
    pass


# ─── Logging ──────────────────────────────────────────────────────────────────

LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
