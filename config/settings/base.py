"""
GREEN NARODA • CLEAN NARODA
============================
Base Settings — Shared across all environments.

Security-sensitive values are NEVER hardcoded here.
All secrets are loaded from environment variables via python-decouple.

Architecture Note:
    This file defines shared configuration only.
    Environment-specific overrides live in development.py and production.py.
    Never import from development.py or production.py directly.
"""

from pathlib import Path

from decouple import Csv, config

# ─── Paths ────────────────────────────────────────────────────────────────────

# Points to the root of the Django project (the `mynaroda/` directory)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ─── Application Definition ───────────────────────────────────────────────────

DJANGO_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "axes",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "cloudinary",
    "cloudinary_storage",
    "django_celery_beat",
    "django_celery_results",
    "whitenoise.runserver_nostatic",
]

LOCAL_APPS = [
    "core",
    "apps.accounts",
    "apps.trees",
    "apps.gallery",
    "apps.events",
    "apps.volunteers",
    "apps.certificates",
    "apps.cms",
    "apps.notifications",
    "apps.news",
    "apps.competitions",
    "apps.student_portal",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ─── Middleware ───────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",          # Static files in production
    "corsheaders.middleware.CorsMiddleware",               # CORS — must be before CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",           # i18n locale detection
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",        # django-allauth
    "core.middleware.RequestLoggingMiddleware",            # Custom audit logging
    "axes.middleware.AxesMiddleware",                      # Security: Rate limiting
]


# ─── URL Configuration ────────────────────────────────────────────────────────

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ─── Templates ────────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "apps.cms.context_processors.site_settings",   # Global CMS data
            ],
        },
    },
]


# ─── Authentication ───────────────────────────────────────────────────────────

# Custom user model — must be set before any migrations
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "axes.backends.AxesBackend",
]

# Site framework — required by allauth
SITE_ID = 1

# Login / Logout redirects
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# ─── Password Validation ──────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ─── REST Framework ───────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}


# ─── django-allauth Configuration ────────────────────────────────────────────

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.accounts.adapters.SocialAccountAdapter"

# Fix "User has no field named username"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SIGNUP_FORM_CLASS = "apps.accounts.forms.CustomSignupForm"

# Fix "SocialApp.DoesNotExist" by using settings-based app config
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": "dummy_client_id_for_dev",
            "secret": "dummy_secret_for_dev",
            "key": ""
        }
    }
}


# ─── Internationalization ─────────────────────────────────────────────────────

import django.conf.locale

# Site supports three languages: English, Gujarati, Hindi
LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("gu", "ગુજરાતી"),
    ("hi", "हिन्दी"),
]

EXTRA_LANG_INFO = {
    "gu": {
        "bidi": False,
        "code": "gu",
        "name": "Gujarati",
        "name_local": "ગુજરાતી",
    },
}
# Add custom languages not provided by Django
django.conf.locale.LANG_INFO.update(EXTRA_LANG_INFO)

TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]


# ─── Static Files ─────────────────────────────────────────────────────────────

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ─── Media Files ──────────────────────────────────────────────────────────────

# In production, Cloudinary handles all media uploads
# In development, files are stored locally under /media/
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ─── Cloudinary Configuration ─────────────────────────────────────────────────

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


# ─── Email Configuration ──────────────────────────────────────────────────────

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default="Green Naroda <noreply@mynaroda.in>"
)


# ─── Celery Configuration ─────────────────────────────────────────────────────

CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# ─── Cache Configuration ──────────────────────────────────────────────────────

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),
    }
}


# ─── Session Configuration ────────────────────────────────────────────────────

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 1800  # 30 mins (Security)


# ─── CSRF Configuration ───────────────────────────────────────────────────────

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://mynaroda.in,https://www.mynaroda.in",
    cast=Csv(),
)


# ─── CORS Configuration ───────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True


# ─── Campaign Constants ───────────────────────────────────────────────────────

# 80th Independence Day: August 15, 2027
# Days from Aug 15, 1947 to Aug 15, 2027 = 28,855 days
CAMPAIGN_TREE_GOAL = 28_855
CAMPAIGN_INDEPENDENCE_YEAR = 80
CAMPAIGN_TARGET_DATE = "2027-08-15"


# ─── Logging ──────────────────────────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# ─── Default Primary Key ──────────────────────────────────────────────────────

# All models that don't explicitly define a PK will use BigAutoField.
# Models requiring UUIDs define them explicitly using core.models.UUIDModel.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


import datetime

# ─── Django Axes Configuration (Security) ─────────────────────────────────────
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = datetime.timedelta(seconds=30)  # 30-second lockout
AXES_LOCK_OUT_AT_FAILURE = True
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_CALLABLE = "apps.admin_panel.views.axes_lockout_view"
AXES_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR',
]


# ─── Django Unfold Theme Configuration ────────────────────────────────────────

UNFOLD = {
    "SITE_TITLE": "Green Naroda • Clean Naroda",
    "SITE_HEADER": "Government Mission Portal",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "/static/images/logo_light.svg",
        "dark": lambda request: "/static/images/logo_dark.svg",
    },
    "COLORS": {
        "primary": {
            "50": "240 253 244",
            "100": "220 252 231",
            "200": "187 247 208",
            "300": "134 239 172",
            "400": "74 222 128",
            "500": "34 197 94",
            "600": "22 163 74",
            "700": "21 128 61",
            "800": "22 101 52",
            "900": "20 83 45",
        }
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "🏠 Control Room",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/dashboard/",
                    },
                ],
            },
            {
                "title": "🌱 Campaign",
                "separator": True,
                "items": [
                    {
                        "title": "Campaign Progress",
                        "icon": "trending_up",
                        "link": "/admin/cms/campaignprogress/",
                    },
                    {
                        "title": "Live Counters",
                        "icon": "speed",
                        "link": "/admin/cms/sitesettings/",
                    },
                    {
                        "title": "Hero Slider",
                        "icon": "view_carousel",
                        "link": "/admin/cms/homepage/",
                    },
                    {
                        "title": "Homepage Sections",
                        "icon": "home",
                        "link": "/admin/cms/homepage/",
                    },
                ],
            },
            {
                "title": "🧾 Pledges",
                "separator": True,
                "items": [
                    {
                        "title": "All Pledges",
                        "icon": "how_to_reg",
                        "link": "/admin/volunteers/pledgeregistration/",
                    },
                    {
                        "title": "Certificates",
                        "icon": "workspace_premium",
                        "link": "/admin/certificates/certificate/",
                    },
                    {
                        "title": "Organizations",
                        "icon": "corporate_fare",
                        "link": "/admin/volunteers/organization/",
                    },
                ],
            },
            {
                "title": "🏢 Competitions",
                "separator": True,
                "items": [
                    {
                        "title": "All Registrations",
                        "icon": "emoji_events",
                        "link": "/admin/competitions/competitionregistration/",
                    },
                    {
                        "title": "Schools",
                        "icon": "school",
                        "link": "/admin/competitions/competitionregistration/?organization_type__exact=SCHOOL",
                    },
                    {
                        "title": "Colleges",
                        "icon": "account_balance",
                        "link": "/admin/competitions/competitionregistration/?organization_type__exact=COLLEGE",
                    },
                    {
                        "title": "Societies",
                        "icon": "apartment",
                        "link": "/admin/competitions/competitionregistration/?organization_type__exact=SOCIETY",
                    },
                    {
                        "title": "NGOs / Trusts",
                        "icon": "handshake",
                        "link": "/admin/competitions/competitionregistration/?organization_type__exact=NGO",
                    },
                    {
                        "title": "Pending Review",
                        "icon": "pending_actions",
                        "link": "/admin/competitions/competitionregistration/?status__exact=PENDING",
                    },
                ],
            },
            {
                "title": "🖼️ Gallery",
                "separator": True,
                "items": [
                    {
                        "title": "⏳ Pending Approval",
                        "icon": "fact_check",
                        "link": "/admin/gallery/photo/?approval_status__exact=PENDING",
                    },
                    {
                        "title": "✓ Approved Photos",
                        "icon": "check_circle",
                        "link": "/admin/gallery/photo/?approval_status__exact=APPROVED",
                    },
                    {
                        "title": "✗ Rejected Photos",
                        "icon": "cancel",
                        "link": "/admin/gallery/photo/?approval_status__exact=REJECTED",
                    },
                    {
                        "title": "All Photos",
                        "icon": "collections",
                        "link": "/admin/gallery/photo/",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": "/admin/gallery/gallerycategory/",
                    },
                ],
            },
            {
                "title": "📰 Content Management",
                "separator": True,
                "items": [
                    {
                        "title": "News Articles",
                        "icon": "article",
                        "link": "/admin/news/newsarticle/",
                    },
                    {
                        "title": "Events",
                        "icon": "event",
                        "link": "/admin/events/event/",
                    },
                    {
                        "title": "FAQs",
                        "icon": "quiz",
                        "link": "/admin/cms/faq/",
                    },
                    {
                        "title": "Partners",
                        "icon": "groups",
                        "link": "/admin/cms/partner/",
                    },
                    {
                        "title": "Testimonials",
                        "icon": "format_quote",
                        "link": "/admin/cms/testimonial/",
                    },
                    {
                        "title": "Media Library",
                        "icon": "perm_media",
                        "link": "/admin/cms/mediaasset/",
                    },
                ],
            },
            {
                "title": "📧 Missions",
                "separator": True,
                "items": [
                    {
                        "title": "Green Naroda",
                        "icon": "forest",
                        "link": "/admin/cms/pagemission/?slug=green-naroda",
                    },
                    {
                        "title": "Clean Naroda",
                        "icon": "cleaning_services",
                        "link": "/admin/cms/pagemission/?slug=clean-naroda",
                    },
                    {
                        "title": "Contact Messages",
                        "icon": "mail",
                        "link": "/admin/cms/contactmessage/",
                    },
                ],
            },
            {
                "title": "👥 Users & Security",
                "separator": True,
                "items": [
                    {
                        "title": "Admin Users",
                        "icon": "admin_panel_settings",
                        "link": "/admin/accounts/user/?is_staff__exact=1",
                    },
                    {
                        "title": "All Users",
                        "icon": "group",
                        "link": "/admin/accounts/user/",
                    },
                    {
                        "title": "Audit Logs",
                        "icon": "history",
                        "link": "/admin/accounts/adminauditlog/",
                    },
                    {
                        "title": "Security & Devices",
                        "icon": "security",
                        "link": "/admin/accounts/devicefingerprint/",
                    },
                ],
            },
            {
                "title": "⚙️ Settings",
                "separator": True,
                "items": [
                    {
                        "title": "Site Settings",
                        "icon": "settings",
                        "link": "/admin/cms/sitesettings/",
                    },
                    {
                        "title": "System Backup",
                        "icon": "cloud_download",
                        "link": "/admin/system/backup/",
                    },
                ],
            },
        ],
    },
}
