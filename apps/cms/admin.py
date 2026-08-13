"""
CMS App — Admin Configuration
==============================
"""

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline

from apps.cms.models import (
    Partner, SiteSettings, Testimonial, ContactMessage,
    MediaAsset, PageMission, PageObjective, PageHighlight, 
    PageActivity, PageStatistic, PageTimeline,
    Homepage, CampaignProgress, HeroSlide, CampaignStatistics
)


@admin.register(CampaignStatistics)
class CampaignStatisticsAdmin(ModelAdmin):
    """
    Singleton admin for Campaign Statistics.
    Hides 'Add' button if one already exists.
    """
    list_display = ("__str__", "cleanliness_drives", "waste_removed_tons")

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    """
    Singleton admin for SiteSettings.
    Hides 'Add' button if one already exists.
    """
    list_display = ("__str__", "popup_enabled", "trees_planted", "volunteers_count", "events_count")

    fieldsets = (
        ("🎯 Campaign Popup", {
            "fields": (
                "popup_enabled",
                "popup_delay_seconds",
                "popup_frequency",
                "campaign_title",
                "popup_message",
                "registration_dates",
                "max_trees_per_registrant",
            )
        }),
        ("📊 Campaign Stats (Legacy — Use Campaign Progress for live counters)", {
            "fields": ("trees_planted", "volunteers_count", "events_count", "photos_count"),
            "classes": ("collapse",),
        }),
        ("🌿 Hero Tagline", {
            "fields": ("hero_tagline_en", "hero_tagline_gu", "hero_tagline_hi"),
        }),
        ("🔗 Social Media Links", {
            "fields": ("facebook_url", "instagram_url", "twitter_url", "youtube_url"),
        }),
        ("📞 Contact Information", {
            "fields": ("contact_email", "contact_phone"),
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ("name", "role", "is_active", "sort_order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "role", "quote_en", "quote_gu", "quote_hi")
    list_editable = ("is_active", "sort_order")
    ordering = ("sort_order", "-created_at")



@admin.register(Partner)
class PartnerAdmin(ModelAdmin):
    list_display = ("name", "website_url", "is_active", "sort_order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active", "sort_order")
    ordering = ("sort_order", "-created_at")


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ("name", "email", "subject", "is_resolved", "created_at")
    list_filter = ("is_resolved",)
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("is_resolved",)
    ordering = ("-created_at",)


from django.utils.html import format_html

# ─── Media Library ────────────────────────────────────────────────────────────

@admin.register(MediaAsset)
class MediaAssetAdmin(ModelAdmin):
    list_display = ("preview_thumbnail", "__str__", "category", "file_size", "created_at")
    search_fields = ("title", "alt_text", "tags")
    list_filter = ("category", "created_at")
    list_display_links = ("__str__",)
    
    def preview_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 40px; border-radius: 4px;" />', obj.image.url)
        return "-"
    preview_thumbnail.short_description = "Preview"


# ─── Dynamic Pages ────────────────────────────────────────────────────────────

class PageObjectiveInline(StackedInline):
    model = PageObjective
    extra = 1

class PageHighlightInline(StackedInline):
    model = PageHighlight
    extra = 1

class PageActivityInline(StackedInline):
    model = PageActivity
    extra = 1

class PageStatisticInline(TabularInline):
    model = PageStatistic
    extra = 1

class PageTimelineInline(StackedInline):
    model = PageTimeline
    extra = 1

@admin.register(PageMission)
class PageMissionAdmin(ModelAdmin):
    list_display = ("title", "slug", "created_at", "updated_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    
    inlines = [
        PageObjectiveInline,
        PageHighlightInline,
        PageActivityInline,
        PageStatisticInline,
        PageTimelineInline,
    ]
    
    fieldsets = (
        ("General Info", {
            "fields": ("title", "slug")
        }),
        ("Hero Section", {
            "fields": ("hero_title", "hero_subtitle", "hero_description", "hero_background")
        }),
        ("Mission Introduction", {
            "fields": ("intro_title", "intro_text_1", "intro_text_2", "intro_image")
        }),
        ("Mission Vision", {
            "fields": ("vision_title", "vision_text", "vision_image")
        }),
        ("SEO / Meta", {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",)
        }),
    )

class HeroSlideInline(StackedInline):
    model = HeroSlide
    extra = 1
    fieldsets = (
        ("Content", {
            "fields": ("title", "subtitle", "description", "image", "mission_type")
        }),
        ("Buttons", {
            "fields": (
                ("primary_button_text", "primary_button_url"),
                ("secondary_button_text", "secondary_button_url")
            )
        }),
        ("Display", {
            "fields": ("is_active", "sort_order")
        }),
    )

@admin.register(Homepage)
class HomepageAdmin(ModelAdmin):
    list_display = ("__str__", "hero_title", "updated_at")
    inlines = [HeroSlideInline]
    fieldsets = (
        ("Legacy Static Hero (Deprecated)", {
            "fields": ("hero_title", "hero_subtitle", "hero_description", "hero_background"),
            "classes": ("collapse",)
        }),
        ("Green Naroda Card", {
            "fields": ("green_card_title", "green_card_text", "green_card_image")
        }),
        ("Clean Naroda Card", {
            "fields": ("clean_card_title", "clean_card_text", "clean_card_image")
        }),
    )
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(CampaignProgress)
class CampaignProgressAdmin(ModelAdmin):
    list_display = ("__str__", "target_trees", "trees_planted", "citizens_joined", "wards_covered", "co2_saved_kg")

    fieldsets = (
        ("🌳 Tree Campaign", {
            "description": "⚡ Changes here reflect INSTANTLY on the public website homepage.",
            "fields": ("target_trees", "trees_planted"),
        }),
        ("👥 Community Engagement", {
            "description": "⚡ Changes here reflect INSTANTLY on the public website homepage.",
            "fields": ("citizens_joined", "wards_covered"),
        }),
        ("🌿 Environmental Impact", {
            "description": "⚡ Changes here reflect INSTANTLY on the public website homepage.",
            "fields": ("co2_saved_kg",),
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


