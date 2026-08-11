"""
Gallery App — Models
=====================
Photo gallery for the Green Naroda campaign.

Features:
    - Cloudinary-backed storage (public_id stored, not file paths)
    - Category and tag taxonomy
    - Approval workflow (photos require admin approval before public display)
    - EXIF metadata extraction at upload time
    - Featured photos for homepage highlights
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UUIDSoftDeleteModel, TimeStampedModel


class GalleryCategory(TimeStampedModel):
    """Taxonomy for organising photos by campaign theme."""

    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True, default="")
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        verbose_name = _("gallery category")
        verbose_name_plural = _("gallery categories")
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class PhotoTag(TimeStampedModel):
    """Free-form tags for photos (e.g. 'neem', 'naroda-patiya', 'school')."""

    name = models.CharField(_("name"), max_length=50, unique=True)
    slug = models.SlugField(_("slug"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("photo tag")
        verbose_name_plural = _("photo tags")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Photo(UUIDSoftDeleteModel):
    """
    A single photograph in the campaign gallery.

    Upload Sources supported (handled at the service layer):
        - Direct file upload (phone/desktop)
        - Drag & drop
        - Image URL
        - Google Drive link
        - Bulk upload

    The approval workflow:
        PENDING → Admin reviews → APPROVED (public) or REJECTED
    """

    class ApprovalStatus(models.TextChoices):
        PENDING = "PENDING", _("Pending Review")
        APPROVED = "APPROVED", _("Approved")
        REJECTED = "REJECTED", _("Rejected")

    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", _("Image")
        DRONE = "DRONE", _("Drone Photo")
        VIDEO = "VIDEO", _("Video")
        PANORAMA = "PANORAMA", _("360 Panorama")

    media_type = models.CharField(
        _("media type"),
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )

    # ── Cloudinary Fields ─────────────────────────────────────────────────────

    cloudinary_id = models.CharField(
        _("Cloudinary ID"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Cloudinary public_id for the original image."),
    )
    url = models.URLField(
        _("URL"),
        blank=True,
        default="",
        help_text=_("Cloudinary delivery URL for the full-size image."),
    )
    local_image = models.ImageField(
        _("uploaded image"),
        upload_to="gallery/uploads/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Direct file upload stored locally (used when Cloudinary is not configured)."),
    )
    thumbnail_url = models.URLField(
        _("thumbnail URL"),
        blank=True,
        default="",
        help_text=_("Cloudinary URL for 400px thumbnail (auto-generated)."),
    )
    webp_url = models.URLField(
        _("WebP URL"),
        blank=True,
        default="",
        help_text=_("Cloudinary WebP format URL for modern browsers."),
    )
    width = models.PositiveIntegerField(_("width"), default=0)
    height = models.PositiveIntegerField(_("height"), default=0)

    # ── Metadata ──────────────────────────────────────────────────────────────

    title = models.CharField(
        _("title"),
        max_length=200,
        blank=True,
        default="",
    )
    photographer = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="photos",
        verbose_name=_("photographer"),
    )
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="photos",
        verbose_name=_("category"),
    )
    tags = models.ManyToManyField(
        PhotoTag,
        blank=True,
        related_name="photos",
        verbose_name=_("tags"),
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="photos",
        verbose_name=_("associated event"),
    )
    location = models.CharField(
        _("location"),
        max_length=200,
        blank=True,
        default="",
    )
    taken_at = models.DateField(
        _("taken on"),
        null=True,
        blank=True,
    )
    exif_data = models.JSONField(
        _("EXIF data"),
        default=dict,
        blank=True,
        help_text=_("Raw EXIF metadata extracted at upload time."),
    )

    # ── Approval & Display ────────────────────────────────────────────────────

    approval_status = models.CharField(
        _("approval status"),
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        db_index=True,
    )
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_photos",
        verbose_name=_("approved by"),
    )
    approved_at = models.DateTimeField(
        _("approved at"),
        null=True,
        blank=True,
    )
    is_featured = models.BooleanField(
        _("featured"),
        default=False,
        db_index=True,
        help_text=_("Featured photos appear in homepage preview."),
    )
    view_count = models.PositiveIntegerField(
        _("view count"),
        default=0,
        help_text=_("Number of times this photo has been viewed."),
    )

    class Meta:
        verbose_name = _("photo")
        verbose_name_plural = _("photos")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["approval_status", "is_featured"]),
            models.Index(fields=["photographer"]),
            models.Index(fields=["category"]),
            models.Index(fields=["taken_at"]),
        ]

    def __str__(self) -> str:
        return self.title or f"Photo {str(self.id)[:8]}"


class GalleryCollection(TimeStampedModel):
    """A collection or album of media items."""

    title = models.CharField(_("title"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=220, unique=True)
    description = models.TextField(_("description"), blank=True, default="")
    cover_photo = models.ForeignKey(
        Photo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="covered_collections",
        verbose_name=_("cover photo"),
    )
    is_published = models.BooleanField(_("published"), default=False)
    photos = models.ManyToManyField(
        Photo,
        blank=True,
        related_name="collections",
        verbose_name=_("photos"),
    )

    class Meta:
        verbose_name = _("gallery collection")
        verbose_name_plural = _("gallery collections")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
