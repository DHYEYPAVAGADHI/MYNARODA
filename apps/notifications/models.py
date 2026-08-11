"""
Notifications App — Models
==========================
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UUIDSoftDeleteModel


class Notification(UUIDSoftDeleteModel):
    """System and user notifications."""
    
    class NotificationType(models.TextChoices):
        INFO = "INFO", _("Information")
        SUCCESS = "SUCCESS", _("Success")
        WARNING = "WARNING", _("Warning")
        ERROR = "ERROR", _("Error")

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("user"),
    )
    notification_type = models.CharField(
        _("type"),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )
    title = models.CharField(_("title"), max_length=200)
    message = models.TextField(_("message"))
    link = models.CharField(_("link"), max_length=255, blank=True, default="")
    is_read = models.BooleanField(_("read"), default=False)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.user.email}"
