"""
Events App — Enhanced Admin Configuration
==========================================
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action

from apps.events.models import Event, EventRegistration


class EventRegistrationInline(TabularInline):
    model = EventRegistration
    extra = 0
    fields = ("user", "attended", "trees_planted", "is_cancelled", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "event_type_badge",
        "starts_at",
        "ends_at",
        "location_name",
        "status_badge",
        "published_badge",
        "trees_target",
        "created_at",
    )
    list_filter = (
        "is_published",
        "event_type",
        "status",
        ("starts_at", admin.DateFieldListFilter),
    )
    search_fields = ("title", "description", "location_name")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    ordering = ("-starts_at",)
    date_hierarchy = "starts_at"
    list_per_page = 25
    inlines = [EventRegistrationInline]
    actions = ["publish_events", "unpublish_events", "mark_completed"]

    fieldsets = (
        ("Event Details", {
            "fields": ("title", "slug", "event_type", "description"),
        }),
        ("Schedule & Venue", {
            "fields": (("starts_at", "ends_at"), "location_name", ("latitude", "longitude")),
        }),
        ("Campaign Impact", {
            "fields": ("trees_target", "max_volunteers", "organiser"),
        }),
        ("Publishing", {
            "fields": ("is_published", "status", "cover_cloudinary_id"),
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at", "deleted_at"),
            "classes": ("collapse",),
        }),
    )

    def cover_thumb(self, obj):
        if obj.cover_cloudinary_id:
            url = f"https://res.cloudinary.com/demo/image/upload/w_64,h_44,c_fill/{obj.cover_cloudinary_id}"
            return format_html(
                '<img src="{}" style="height:44px;width:64px;object-fit:cover;border-radius:6px;" />',
                url
            )
        return format_html('<span style="color:#9CA3AF;font-size:1.5rem;">📅</span>')
    cover_thumb.short_description = "Cover"

    def status_badge(self, obj):
        colors = {
            "UPCOMING": ("#EFF6FF", "#2563EB", "🗓️ Upcoming"),
            "ONGOING": ("#F0FDF4", "#16A34A", "🔴 Ongoing"),
            "COMPLETED": ("#F3F4F6", "#6B7280", "✓ Completed"),
            "CANCELLED": ("#FEF2F2", "#DC2626", "✗ Cancelled"),
        }
        bg, fg, label = colors.get(obj.status, ("#F3F4F6", "#6B7280", obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:999px;'
            'font-size:0.7rem;font-weight:700;">{}</span>',
            bg, fg, label
        )
    status_badge.short_description = "Status"

    def event_type_badge(self, obj):
        icons = {
            "PLANTATION": "🌱",
            "AWARENESS": "📢",
            "CLEANUP": "🧹",
            "CELEBRATION": "🎉",
            "OTHER": "📌",
        }
        icon = icons.get(obj.event_type, "📌")
        return format_html(
            '<span style="font-size:0.8125rem;">{} {}</span>',
            icon, obj.get_event_type_display()
        )
    event_type_badge.short_description = "Type"

    def published_badge(self, obj):
        if obj.is_published:
            return format_html(
                '<span style="background:#DCFCE7;color:#16A34A;padding:2px 8px;'
                'border-radius:999px;font-size:0.7rem;font-weight:700;">Live</span>'
            )
        return format_html(
            '<span style="background:#F3F4F6;color:#9CA3AF;padding:2px 8px;'
            'border-radius:999px;font-size:0.7rem;font-weight:700;">Draft</span>'
        )
    published_badge.short_description = "Published"

    @action(description=_("📢 Publish selected events"))
    def publish_events(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count} events published.")

    @action(description=_("📥 Unpublish selected events"))
    def unpublish_events(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} events moved to draft.")

    @action(description=_("✓ Mark selected events as Completed"))
    def mark_completed(self, request, queryset):
        count = queryset.update(status=Event.EventStatus.COMPLETED)
        self.message_user(request, f"{count} events marked as completed.")


@admin.register(EventRegistration)
class EventRegistrationAdmin(ModelAdmin):
    list_display = ("event", "user", "attended", "trees_planted", "is_cancelled", "created_at")
    list_filter = ("attended", "is_cancelled", ("created_at", admin.DateFieldListFilter))
    search_fields = ("event__title", "user__email", "user__full_name")
    ordering = ("-created_at",)
    list_per_page = 25
