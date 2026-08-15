"""
URL Configuration — Root Router
=================================
All URL patterns are namespaced by application.

Pattern Conventions:
    /                           → Landing page
    /admin/                     → Custom Mission Control admin panel
    /django-admin/              → Django's built-in admin (dev only)
    /accounts/                  → Authentication (allauth + custom)
    /api/v1/                    → REST API (versioned)
    /gallery/                   → Photo gallery
    /events/                    → Events
    /volunteers/                → Volunteer portal
    /i18n/                      → Language switching (built-in Django)
    /silk/                      → Profiler (dev only)
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from apps.volunteers.views import VerifyCertificateView
from apps.admin_panel.views import PublicStatsAPIView


# ─── Admin Customization ──────────────────────────────────────────────────────

admin.site.site_header = "mynaroda | Django Admin"
admin.site.site_title = "mynaroda"
admin.site.index_title = "Green Naroda Campaign Management"


# ─── Non-localised URL patterns ──────────────────────────────────────────────
# These URLs do not carry a language prefix (e.g., /api/v1/)

urlpatterns = [
    # ── Custom Mission Control Admin Panel ───────────────────────────────────
    # /admin/ → our premium custom panel (NOT Django's default admin)
    path("admin/", include("apps.admin_panel.urls", namespace="admin_panel")),

    # ── Django's built-in admin moved to /django-admin/ ─────────────────────
    path("django-admin/", admin.site.urls),

    # ── Public Stats API (used by homepage live counters) ────────────────────
    path("api/stats/", PublicStatsAPIView.as_view(), name="public_stats_api"),

    # ── Django Allauth ───────────────────────────────────────────────────────
    path("accounts/", include("allauth.urls")),

    # ── Custom authentication views (OTP, etc.) ──────────────────────────────
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),

    # ── REST API — versioned ─────────────────────────────────────────────────
    path("api/v1/", include("apps.accounts.api_urls", namespace="accounts-api")),
    path("api/v1/trees/", include("apps.trees.api_urls", namespace="trees-api")),
    path("api/v1/gallery/", include("apps.gallery.api_urls", namespace="gallery-api")),
    path("api/v1/events/", include("apps.events.api_urls", namespace="events-api")),
    path("api/v1/volunteers/", include("apps.volunteers.api_urls", namespace="volunteers-api")),

    # ── Custom root-level APIs ───────────────────────────────────────────────
    path("api/", include("apps.competitions.api_urls", namespace="competitions-api")),

    # ── Language switching (AJAX-friendly) ───────────────────────────────────
    path("i18n/", include("django.conf.urls.i18n")),
]

# ─── Localised URL patterns ───────────────────────────────────────────────────
# These carry an optional language prefix: /en/, /gu/, /hi/

urlpatterns += i18n_patterns(
    path("verify/<path:certificate_id>/", VerifyCertificateView.as_view(), name="verify_certificate"),

    # Organization QR Verification
    path("verify/organization/<str:registration_id>/", include("apps.competitions.verify_urls")),

    path("student-portal/", include("apps.student_portal.urls")),
    path("", include("apps.cms.urls", namespace="cms")),

    # Tree tracker
    path("trees/", include("apps.trees.urls", namespace="trees")),

    # Photo gallery
    path("gallery/", include("apps.gallery.urls", namespace="gallery")),

    # Events
    path("events/", include("apps.events.urls", namespace="events")),

    # Volunteers
    path("volunteers/", include("apps.volunteers.urls", namespace="volunteers")),

    # Competitions
    path("competition-registration/", include("apps.competitions.urls", namespace="competitions")),

    # User certificates
    path("certificates/", include("apps.certificates.urls", namespace="certificates")),

    # News & Press releases
    path("news/", include("apps.news.urls", namespace="news")),

    prefix_default_language=False,  # Default language (English) has no prefix
)


# ─── Debug-only URLs ──────────────────────────────────────────────────────────

if settings.DEBUG:
    try:
        import debug_toolbar

        # Development-only mock Google OAuth (logs in as any email WITHOUT a
        # password). MUST NEVER be exposed in production — it is an auth bypass.
        from apps.accounts.views import MockGoogleLoginView

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            path("auth/mock-google-login/", MockGoogleLoginView.as_view(), name="mock_google_login"),
        ] + urlpatterns
    except ImportError:
        pass

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
