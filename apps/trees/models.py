"""
Trees App — Models
===================
Data models for the tree plantation tracker.

Every tree planted during the Green Naroda campaign has:
    - A unique UUID identifier
    - A QR code for field verification
    - Geographic coordinates
    - A species record
    - Contribution and planting details
    - Photo documentation
    - A verification workflow

Design:
    Tree and TreePhoto use UUIDSoftDeleteModel (UUID PK + soft delete).
    TreeVerification uses BigAutoField PK (internal operational record).
    TreeSpecies uses BigAutoField (small reference table, no public exposure).
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, UUIDSoftDeleteModel
from core.validators import validate_latitude, validate_longitude


# ─── Tree Species ─────────────────────────────────────────────────────────────


class TreeSpecies(TimeStampedModel):
    """
    Reference table of tree species used in the campaign.

    Maintained by Coordinators and Admins.
    Provides scientific classification and care instructions.
    """

    name = models.CharField(
        _("common name"),
        max_length=100,
        unique=True,
        help_text=_("Common name of the species (e.g. Neem, Peepal)."),
    )
    scientific_name = models.CharField(
        _("scientific name"),
        max_length=150,
        blank=True,
        default="",
        help_text=_("Binomial scientific name (e.g. Azadirachta indica)."),
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
        help_text=_("Brief ecological description and care notes."),
    )
    native_to_gujarat = models.BooleanField(
        _("native to Gujarat"),
        default=False,
        help_text=_("True if this species is native to the Gujarat region."),
    )
    image_cloudinary_id = models.CharField(
        _("image Cloudinary ID"),
        max_length=255,
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = _("tree species")
        verbose_name_plural = _("tree species")
        ordering = ["name"]

    def __str__(self) -> str:
        if self.scientific_name:
            return f"{self.name} ({self.scientific_name})"
        return self.name


# ─── Verification Status ──────────────────────────────────────────────────────


class VerificationStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending Verification")
    VERIFIED = "VERIFIED", _("Verified")
    REJECTED = "REJECTED", _("Rejected")


class GrowthStage(models.TextChoices):
    SAPLING = "SAPLING", _("Sapling")
    YOUNG = "YOUNG", _("Young Tree")
    MATURE = "MATURE", _("Mature Tree")


class TreeHealth(models.TextChoices):
    EXCELLENT = "EXCELLENT", _("Excellent")
    GOOD = "GOOD", _("Good")
    AVERAGE = "AVERAGE", _("Average")
    POOR = "POOR", _("Poor")
    DEAD = "DEAD", _("Dead")


# ─── Tree ─────────────────────────────────────────────────────────────────────


class Tree(UUIDSoftDeleteModel):
    """
    Central model representing a single planted tree.

    Each tree has a UUID that is encoded into its QR code.
    Scanning the QR takes a user to /trees/<uuid>/ showing the tree's full story.

    Geographic Data:
        Latitude and longitude are stored as FloatField for simplicity.
        If geospatial queries become necessary (e.g. proximity search),
        migrate to PostGIS PointField in a future iteration.

    Verification Workflow:
        PENDING → (Coordinator reviews) → VERIFIED or REJECTED
    """

    # ── Relationship Fields ───────────────────────────────────────────────────

    species = models.ForeignKey(
        TreeSpecies,
        on_delete=models.PROTECT,          # Never lose a tree's species data
        related_name="trees",
        verbose_name=_("species"),
    )
    contributor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contributed_trees",
        verbose_name=_("contributor"),
        help_text=_("The person who sponsored/registered this tree."),
    )
    planted_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="planted_trees",
        verbose_name=_("planted by"),
        help_text=_("The volunteer who physically planted the tree."),
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trees",
        verbose_name=_("planting event"),
    )

    # ── Location Fields ───────────────────────────────────────────────────────

    latitude = models.FloatField(
        _("latitude"),
        validators=[validate_latitude],
        help_text=_("GPS latitude of planting location."),
    )
    longitude = models.FloatField(
        _("longitude"),
        validators=[validate_longitude],
        help_text=_("GPS longitude of planting location."),
    )
    location_name = models.CharField(
        _("location name"),
        max_length=200,
        blank=True,
        default="",
        help_text=_("Human-readable location description (e.g. Near Naroda Patiya)."),
    )
    ward = models.CharField(
        _("ward"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("Ahmedabad Municipal Corporation ward number/name."),
    )

    # ── Tree Data ─────────────────────────────────────────────────────────────

    planted_at = models.DateField(
        _("planted on"),
        help_text=_("The date this tree was physically planted."),
    )
    qr_code_url = models.URLField(
        _("QR code URL"),
        blank=True,
        default="",
        help_text=_("URL to the generated QR code image for this tree."),
    )
    verification_status = models.CharField(
        _("verification status"),
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
    )
    growth_stage = models.CharField(
        _("growth stage"),
        max_length=10,
        choices=GrowthStage.choices,
        default=GrowthStage.SAPLING,
    )
    notes = models.TextField(
        _("notes"),
        blank=True,
        default="",
        help_text=_("Optional notes about this tree (e.g. care instructions, soil type)."),
    )
    health_status = models.CharField(
        _("health status"),
        max_length=20,
        choices=TreeHealth.choices,
        default=TreeHealth.GOOD,
    )

    class Meta:
        verbose_name = _("tree")
        verbose_name_plural = _("trees")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["verification_status"]),
            models.Index(fields=["planted_at"]),
            models.Index(fields=["ward"]),
            models.Index(fields=["contributor"]),
        ]

    def __str__(self) -> str:
        return f"Tree #{str(self.id)[:8]} — {self.species.name} at {self.location_name or 'Unknown'}"

    @property
    def public_url_path(self) -> str:
        """Returns the canonical URL path for this tree's public page."""
        return f"/trees/{self.id}/"

    @property
    def is_verified(self) -> bool:
        return self.verification_status == VerificationStatus.VERIFIED


# ─── Tree Photo ───────────────────────────────────────────────────────────────


class TreePhoto(TimeStampedModel):
    """
    A photograph documenting a specific tree.

    Multiple photos per tree are allowed to track growth over time.
    Photos are stored on Cloudinary; only the public_id is stored here.
    """

    tree = models.ForeignKey(
        Tree,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name=_("tree"),
    )
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="tree_photos",
        verbose_name=_("uploaded by"),
    )
    cloudinary_id = models.CharField(
        _("Cloudinary ID"),
        max_length=255,
        help_text=_("Cloudinary public_id for the photo."),
    )
    cloudinary_url = models.URLField(
        _("Cloudinary URL"),
        help_text=_("Optimised delivery URL from Cloudinary."),
    )
    caption = models.CharField(
        _("caption"),
        max_length=200,
        blank=True,
        default="",
    )
    taken_at = models.DateField(
        _("taken on"),
        null=True,
        blank=True,
        help_text=_("Date the photograph was taken (from EXIF if available)."),
    )
    is_primary = models.BooleanField(
        _("is primary"),
        default=False,
        help_text=_("The primary display photo for this tree."),
    )

    class Meta:
        verbose_name = _("tree photo")
        verbose_name_plural = _("tree photos")
        ordering = ["-created_at"]
        constraints = [
            # Only one primary photo per tree
            models.UniqueConstraint(
                fields=["tree"],
                condition=models.Q(is_primary=True),
                name="unique_primary_photo_per_tree",
            )
        ]

    def __str__(self) -> str:
        return f"Photo of {self.tree} by {self.uploaded_by}"


# ─── Tree Verification ────────────────────────────────────────────────────────


class TreeVerification(TimeStampedModel):
    """
    Records the outcome of a coordinator's field verification of a tree.

    One record per verification event (a tree may be re-verified after rejection).
    """

    tree = models.ForeignKey(
        Tree,
        on_delete=models.CASCADE,
        related_name="verifications",
        verbose_name=_("tree"),
    )
    verified_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="tree_verifications",
        verbose_name=_("verified by"),
    )
    status = models.CharField(
        _("decision"),
        max_length=20,
        choices=VerificationStatus.choices,
    )
    notes = models.TextField(
        _("verification notes"),
        blank=True,
        default="",
        help_text=_("Coordinator's field notes about this verification."),
    )

    class Meta:
        verbose_name = _("tree verification")
        verbose_name_plural = _("tree verifications")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.status} for Tree {self.tree.id} by {self.verified_by.full_name}"


# ─── Tree Maintenance Log ─────────────────────────────────────────────────────


class TreeMaintenanceLog(TimeStampedModel):
    """
    Log of maintenance requests and actions for a tree.
    """
    
    class MaintenanceType(models.TextChoices):
        WATER = "WATER", _("Needs Water")
        SUPPORT = "SUPPORT", _("Needs Support")
        DISEASE = "DISEASE", _("Disease Reported")
        FENCE = "FENCE", _("Fence Broken")
        REPLACEMENT = "REPLACEMENT", _("Replacement Needed")
        OTHER = "OTHER", _("Other")

    tree = models.ForeignKey(
        Tree,
        on_delete=models.CASCADE,
        related_name="maintenance_logs",
        verbose_name=_("tree"),
    )
    reported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_maintenance",
        verbose_name=_("reported by"),
    )
    issue_type = models.CharField(
        _("issue type"),
        max_length=20,
        choices=MaintenanceType.choices,
    )
    description = models.TextField(
        _("description"),
        blank=True,
        default="",
    )
    is_resolved = models.BooleanField(
        _("resolved"),
        default=False,
    )
    resolved_at = models.DateTimeField(
        _("resolved at"),
        null=True,
        blank=True,
    )
    resolved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_maintenance",
        verbose_name=_("resolved by"),
    )

    class Meta:
        verbose_name = _("maintenance log")
        verbose_name_plural = _("maintenance logs")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.issue_type} for Tree {self.tree.id[:8]}"
