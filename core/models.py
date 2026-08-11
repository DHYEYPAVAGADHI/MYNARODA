"""
Core Abstract Models
=====================
Defines the base model hierarchy used across all applications.

Every production model should inherit from one of:

    TimeStampedModel  — Automatic created_at / updated_at timestamps
    SoftDeleteModel   — Soft deletion (never hard-deletes records)
    AuditModel        — Full audit trail (who created/modified)
    UUIDModel         — UUID primary key (for publicly-exposed resources)
    UUIDSoftDeleteModel — UUID + soft delete combined

Design Decisions:
    - UUID PKs are used on models where IDs are exposed in URLs or APIs
      to prevent enumeration attacks.
    - BigAutoField (sequential integer) PKs are used on internal join tables.
    - Soft delete uses a manager to transparently filter deleted records.
    - All timestamps are stored in UTC; displayed in IST via TIME_ZONE setting.
"""

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ─── Managers ─────────────────────────────────────────────────────────────────


class ActiveManager(models.Manager):
    """Returns only non-deleted records. Used as the default manager on SoftDeleteModel."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Returns ALL records, including soft-deleted ones. Used for admin/audit purposes."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset()


# ─── Abstract Models ──────────────────────────────────────────────────────────


class TimeStampedModel(models.Model):
    """
    Abstract base providing automatic `created_at` and `updated_at` timestamps.

    All models in this project inherit from this class at minimum.
    Timestamps are stored in UTC and auto-managed by Django's ORM.
    """

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
        db_index=True,
        help_text=_("The date and time this record was created (UTC)."),
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
        help_text=_("The date and time this record was last modified (UTC)."),
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base adding soft-deletion capability.

    Records are never physically removed from the database.
    Instead, `is_deleted` is set to True and `deleted_at` is recorded.

    Usage:
        MyModel.objects.all()         → only active records (via ActiveManager)
        MyModel.all_objects.all()     → all records including deleted
        instance.delete()             → soft deletes (sets is_deleted=True)
        instance.hard_delete()        → physical delete (use with extreme caution)
        instance.restore()            → un-deletes a record
    """

    is_deleted = models.BooleanField(
        _("is deleted"),
        default=False,
        db_index=True,
        help_text=_("Soft delete flag. Deleted records are hidden from normal queries."),
    )
    deleted_at = models.DateTimeField(
        _("deleted at"),
        null=True,
        blank=True,
        help_text=_("The date and time this record was soft-deleted (UTC)."),
    )

    # Default manager filters out deleted records transparently
    objects = ActiveManager()

    # Access all records (including deleted) via this manager
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False) -> None:  # type: ignore[override]
        """Perform a soft delete instead of a physical DELETE query."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self) -> None:
        """Physically delete the record. Use only in migrations or data cleanup scripts."""
        super().delete()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])


class AuditModel(SoftDeleteModel):
    """
    Abstract base adding audit trail fields (who created / last modified this record).

    `created_by` and `updated_by` are nullable to support system-generated records
    (e.g. records created via management commands or data migrations).
    """

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name=_("last updated by"),
    )

    class Meta:
        abstract = True


class UUIDModel(TimeStampedModel):
    """
    Abstract base using a UUID primary key.

    Used for models whose primary key is exposed in URLs or APIs
    to prevent sequential ID enumeration attacks.

    Example: /trees/a3f1e2d4-... instead of /trees/1/
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("UUID"),
        help_text=_("Unique public identifier for this record."),
    )

    class Meta:
        abstract = True


class UUIDSoftDeleteModel(UUIDModel):
    """
    Combines UUID primary key with soft-deletion capability.

    Use this for publicly-exposed models that should never be hard-deleted.
    Example: Trees, Photos, Certificates.
    """

    is_deleted = models.BooleanField(
        _("is deleted"),
        default=False,
        db_index=True,
    )
    deleted_at = models.DateTimeField(
        _("deleted at"),
        null=True,
        blank=True,
    )

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False) -> None:  # type: ignore[override]
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self) -> None:
        super(UUIDModel, self).delete()

    def restore(self) -> None:
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
