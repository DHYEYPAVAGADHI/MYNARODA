"""
News App — Enhanced Admin Configuration
========================================
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action

from apps.news.models import NewsCategory, NewsArticle, Document


@admin.register(NewsCategory)
class NewsCategoryAdmin(ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsArticle)
class NewsArticleAdmin(ModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "category",
        "published_status_badge",
        "published_at",
        "created_at",
    )
    list_filter = ("is_published", "category", ("published_at", admin.DateFieldListFilter))
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at",)
    date_hierarchy = "published_at"
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    actions = ["publish_articles", "unpublish_articles"]

    fieldsets = (
        ("Article Info", {
            "fields": ("title", "slug", "category", "summary"),
        }),
        ("Content", {
            "fields": ("content", "cover_image_id"),
        }),
        ("Publishing", {
            "fields": ("is_published", "published_at"),
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def cover_thumb(self, obj):
        if obj.cover_image_id:
            url = f"https://res.cloudinary.com/demo/image/upload/w_60,h_44,c_fill/{obj.cover_image_id}"
            return format_html(
                '<img src="{}" style="height:44px;width:60px;object-fit:cover;border-radius:6px;" />',
                url
            )
        return format_html('<span style="color:#9CA3AF;font-size:1.25rem;">📰</span>')
    cover_thumb.short_description = "Cover"

    def published_status_badge(self, obj):
        if obj.is_published:
            return format_html(
                '<span style="background:#DCFCE7;color:#16A34A;padding:3px 10px;'
                'border-radius:999px;font-size:0.7rem;font-weight:700;">✓ Published</span>'
            )
        return format_html(
            '<span style="background:#F3F4F6;color:#6B7280;padding:3px 10px;'
            'border-radius:999px;font-size:0.7rem;font-weight:700;">Draft</span>'
        )
    published_status_badge.short_description = "Status"

    @action(description=_("📢 Publish selected articles"))
    def publish_articles(self, request, queryset):
        count = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, f"{count} articles published and now visible on the website.")

    @action(description=_("📥 Unpublish selected articles"))
    def unpublish_articles(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} articles moved to draft.")


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ("title", "file_url", "is_public", "created_at")
    list_filter = ("is_public",)
    list_editable = ("is_public",)
    search_fields = ("title",)
    ordering = ("-created_at",)
