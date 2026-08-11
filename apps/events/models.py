"""
Events App — Models
====================
Event management for tree plantation drives and campaign gatherings.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UUIDSoftDeleteModel, TimeStampedModel
from core.validators import validate_latitude, validate_longitude


class Event(UUIDSoftDeleteModel):
    """A campaign event (plantation drive, awareness rally, etc.)."""

    class EventType(models.TextChoices):
        PLANTATION = "PLANTATION", _("Tree Plantation Drive")
        AWARENESS = "AWARENESS", _("Awareness Campaign")
        CLEANUP = "CLEANUP", _("Clean-up Drive")
        CELEBRATION = "CELEBRATION", _("Celebration")
        OTHER = "OTHER", _("Other")

    class EventStatus(models.TextChoices):
        UPCOMING = "UPCOMING", _("Upcoming")
        ONGOING = "ONGOING", _("Ongoing")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=220, unique=True)
    event_type = models.CharField(
        _("event type"),
        max_length=20,
        choices=EventType.choices,
        default=EventType.PLANTATION,
    )
    description = models.TextField(_("description"), blank=True, default="")
    location_name = models.CharField(_("location name"), max_length=200)
    latitude = models.FloatField(
        _("latitude"),
        null=True,
        blank=True,
        validators=[validate_latitude],
    )
    longitude = models.FloatField(
        _("longitude"),
        null=True,
        blank=True,
        validators=[validate_longitude],
    )
    starts_at = models.DateTimeField(_("starts at"), db_index=True)
    ends_at = models.DateTimeField(_("ends at"))
    max_volunteers = models.PositiveIntegerField(
        _("max volunteers"),
        null=True,
        blank=True,
        help_text=_("Maximum number of volunteer registrations (null = unlimited)."),
    )
    cover_cloudinary_id = models.CharField(
        _("cover image Cloudinary ID"),
        max_length=255,
        blank=True,
        default="",
    )
    organiser = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organised_events",
        verbose_name=_("organiser"),
    )
    is_published = models.BooleanField(
        _("published"),
        default=False,
        db_index=True,
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.UPCOMING,
        db_index=True,
    )
    trees_target = models.PositiveIntegerField(
        _("trees target"),
        default=0,
        help_text=_("Number of trees planned for this event."),
    )

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        ordering = ["-starts_at"]
        indexes = [
            models.Index(fields=["is_published", "starts_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def registration_count(self) -> int:
        return self.registrations.filter(is_cancelled=False).count()

    @property
    def is_full(self) -> bool:
        if self.max_volunteers is None:
            return False
        return self.registration_count >= self.max_volunteers


class EventRegistration(TimeStampedModel):
    """A volunteer's registration for an event."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name=_("event"),
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="event_registrations",
        verbose_name=_("volunteer"),
    )
    is_cancelled = models.BooleanField(_("cancelled"), default=False)
    attended = models.BooleanField(_("attended"), default=False)
    trees_planted = models.PositiveIntegerField(
        _("trees planted"),
        default=0,
        help_text=_("Trees planted by this volunteer at this event."),
    )
    notes = models.TextField(_("notes"), blank=True, default="")

    class Meta:
        verbose_name = _("event registration")
        verbose_name_plural = _("event registrations")
        unique_together = [["event", "user"]]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.full_name} @ {self.event.title}"
