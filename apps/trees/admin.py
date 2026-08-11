"""
Trees App — Admin Configuration
================================
"""

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.trees.models import Tree, TreePhoto, TreeSpecies, TreeVerification


@admin.register(TreeSpecies)
class TreeSpeciesAdmin(ModelAdmin):
    list_display = ("name", "scientific_name", "native_to_gujarat", "created_at")
    list_filter = ("native_to_gujarat",)
    search_fields = ("name", "scientific_name")
    ordering = ("name",)


class TreePhotoInline(TabularInline):
    model = TreePhoto
    extra = 0
    fields = ("image_cloudinary_id", "uploaded_by", "created_at", "is_primary")
    readonly_fields = ("uploaded_by", "created_at")


class TreeVerificationInline(TabularInline):
    model = TreeVerification
    extra = 0
    fields = ("verified_by", "status", "created_at", "notes")
    readonly_fields = ("created_at",)


@admin.register(Tree)
class TreeAdmin(ModelAdmin):
    list_display = (
        "id",
        "species",
        "ward",
        "verification_status",
        "growth_stage",
        "planted_at",
    )
    list_filter = ("verification_status", "growth_stage", "ward", "species")
    search_fields = ("id", "location_name", "ward", "contributor__email", "contributor__full_name")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    inlines = [TreePhotoInline, TreeVerificationInline]
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("species", "contributor", "planted_at")}),
        (
            "Location",
            {"fields": ("latitude", "longitude", "location_name", "ward")},
        ),
        (
            "Status & Details",
            {
                "fields": (
                    "verification_status",
                    "growth_stage",
                    "qr_code_url",
                    "notes",
                )
            },
        ),
        ("Audit", {"fields": ("created_at", "updated_at", "deleted_at"), "classes": ("collapse",)}),
    )


@admin.register(TreePhoto)
class TreePhotoAdmin(ModelAdmin):
    list_display = ("tree", "uploaded_by", "is_primary", "created_at")
    list_filter = ("is_primary", "created_at")
    search_fields = ("tree__id", "uploaded_by__email")


@admin.register(TreeVerification)
class TreeVerificationAdmin(ModelAdmin):
    list_display = ("tree", "verified_by", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("tree__id", "verified_by__email")
