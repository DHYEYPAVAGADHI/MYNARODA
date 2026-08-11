"""
Accounts App — Admin Configuration
===================================
Custom admin interface for the User model and OTP tokens, using django-unfold.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.accounts.models import OTPToken, User, DeviceFingerprint, AdminAuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Custom admin panel for our UUID-based User model.
    Uses django-unfold styling and replaces standard auth forms.
    """
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        "email",
        "full_name",
        "phone",
        "role",
        "is_verified",
        "is_active",
        "created_at",
    )
    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "full_name", "phone")
    ordering = ("-created_at",)
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("full_name", "phone", "avatar_cloudinary_id")},
        ),
        (
            _("Permissions & Roles"),
            {
                "fields": (
                    "role",
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "password_confirmation"),
            },
        ),
    )


@admin.register(OTPToken)
class OTPTokenAdmin(ModelAdmin):
    """Admin view for OTP tokens (read-only for security)."""
    list_display = ("user", "purpose", "expires_at", "is_used", "created_at")
    list_filter = ("purpose", "is_used", "created_at")
    search_fields = ("user__email", "user__phone")
    readonly_fields = ("user", "code", "purpose", "expires_at", "is_used")
    ordering = ("-created_at",)


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(ModelAdmin):
    list_display = ("user", "ip_address", "user_agent", "is_trusted", "last_login_at")
    list_filter = ("is_trusted", "last_login_at")
    search_fields = ("user__email", "ip_address")
    readonly_fields = ("user", "ip_address", "user_agent", "last_login_at")


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(ModelAdmin):
    list_display = ("user", "action", "model_name", "ip_address", "timestamp")
    list_filter = ("action", "timestamp", "model_name")
    search_fields = ("user__email", "details", "ip_address")
    readonly_fields = ("user", "action", "model_name", "object_id", "details", "ip_address", "user_agent", "timestamp")

    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
