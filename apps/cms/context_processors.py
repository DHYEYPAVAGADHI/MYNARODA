"""
CMS Context Processor
======================
Injects global site settings into every template context.
This avoids passing site_settings manually in every view.

The result is cached for 5 minutes to avoid a DB query on every request.
"""

from django.core.cache import cache


def site_settings(request) -> dict:
    """
    Injects `site_settings` and `TREE_GOAL` into every template context.

    Cache key: 'cms:site_settings' — invalidated whenever SiteSettings is saved.
    """
    from apps.cms.models import SiteSettings, BrandingSettings  # local import to avoid circular deps

    settings_obj = cache.get("cms:site_settings")
    if settings_obj is None:
        settings_obj = SiteSettings.objects.first()
        cache.set("cms:site_settings", settings_obj, timeout=300)  # 5 minutes

    branding_obj = cache.get("cms:branding_settings")
    if branding_obj is None:
        branding_obj = BrandingSettings.load()
        cache.set("cms:branding_settings", branding_obj, timeout=300)

    return {
        "site_settings": settings_obj,
        "branding_settings": branding_obj,
        "TREE_GOAL": 28_855,
    }
