from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.certificates.models import Certificate

@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    list_display = ("certificate_number", "user", "certificate_type", "issued_at")
    list_filter = ("certificate_type", "issued_at")
    search_fields = ("certificate_number", "user__email", "user__full_name")
    readonly_fields = ("issued_at", "certificate_number")
    ordering = ("-issued_at",)
