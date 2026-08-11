"""
Accounts App — User Model
==========================
Custom User model replacing Django's built-in User.

Design Decisions:
    - Email is the primary identifier (not username).
    - Phone is optional but supports OTP-based login when provided.
    - Role is a string enum stored as CharField for simplicity and readability.
    - UUID primary key prevents user ID enumeration.
    - `is_verified` tracks email verification status (not to be confused with
      Django's `is_active` which controls login access entirely).

Security Notes:
    - Passwords are hashed by Django's PBKDF2 by default (configurable).
    - Phone numbers are stored in E.164 format.
    - Avatar URLs are stored (Cloudinary public_id), not file paths.
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.validators import validate_indian_phone


# ─── Role Definitions ─────────────────────────────────────────────────────────


class UserRole(models.TextChoices):
    """
    Ordered hierarchy of roles from least to most privileged.
    Role checks should use >= comparisons via role_rank() when needed.
    """

    GUEST = "GUEST", _("Guest")
    CITIZEN = "CITIZEN", _("Citizen")
    VOLUNTEER = "VOLUNTEER", _("Volunteer")
    PHOTOGRAPHER = "PHOTOGRAPHER", _("Photographer")
    COORDINATOR = "COORDINATOR", _("Coordinator")
    ORGANIZER = "ORGANIZER", _("Organizer")
    ADMIN = "ADMIN", _("Admin")
    SUPER_ADMIN = "SUPER_ADMIN", _("Super Admin")


class VolunteerLevel(models.TextChoices):
    """
    Gamification levels based on volunteer activity.
    """
    SEED = "SEED", _("Seed Volunteer")
    GREEN = "GREEN", _("Green Volunteer")
    GUARDIAN = "GUARDIAN", _("Tree Guardian")
    CHAMPION = "CHAMPION", _("Nature Champion")
    AMBASSADOR = "AMBASSADOR", _("Green Ambassador")


# ─── User Manager ─────────────────────────────────────────────────────────────


class UserManager(BaseUserManager):
    """Custom manager for the User model with email-based authentication."""

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ) -> "User":
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_("An email address is required."))
        email = self.normalize_email(email)
        extra_fields.setdefault("role", UserRole.CITIZEN)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields,
    ) -> "User":
        """Create and save a superuser with all flags set."""
        extra_fields.setdefault("role", UserRole.SUPER_ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


# ─── User Model ───────────────────────────────────────────────────────────────


class User(AbstractBaseUser, PermissionsMixin):
    """
    Primary user model for the Green Naroda platform.

    Authentication Methods supported:
        1. Email + Password
        2. Google OAuth (via django-allauth SocialAccount)
        3. Phone + OTP (via OTPToken)
    """

    # ── Identity ──────────────────────────────────────────────────────────────

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("UUID"),
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,
        help_text=_("Primary login identifier. Must be unique."),
    )
    phone = models.CharField(
        _("phone number"),
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_indian_phone],
        help_text=_("Optional. Indian mobile number in E.164 format (+91XXXXXXXXXX)."),
    )
    full_name = models.CharField(
        _("full name"),
        max_length=150,
        help_text=_("User's display name."),
    )

    # ── Profile ───────────────────────────────────────────────────────────────

    avatar_cloudinary_id = models.CharField(
        _("avatar Cloudinary ID"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Cloudinary public_id for the profile picture."),
    )
    bio = models.TextField(
        _("bio"),
        blank=True,
        default="",
        max_length=500,
        help_text=_("Short user biography (max 500 characters)."),
    )
    city = models.CharField(
        _("city"),
        max_length=100,
        default="Naroda",
        help_text=_("User's city. Defaults to Naroda."),
    )

    # ── Volunteer Gamification ────────────────────────────────────────────────

    volunteer_level = models.CharField(
        _("volunteer level"),
        max_length=20,
        choices=VolunteerLevel.choices,
        default=VolunteerLevel.SEED,
    )
    total_hours = models.PositiveIntegerField(
        _("total volunteer hours"),
        default=0,
    )
    trees_planted = models.PositiveIntegerField(
        _("trees planted"),
        default=0,
    )

    # ── Permissions & State ─────────────────────────────────────────────────────────

    role = models.CharField(
        _("role"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CITIZEN,
        db_index=True,
        help_text=_("User's access role."),
    )
    is_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("True when the user has confirmed their email address."),
    )
    is_phone_verified = models.BooleanField(
        _("phone verified"),
        default=False,
        help_text=_("True when the user has confirmed their mobile phone number."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active. "
                    "Unselect this instead of deleting accounts."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )

    # ── Timestamps ────────────────────────────────────────────────────────────

    created_at = models.DateTimeField(_("joined"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("last updated"), auto_now=True)
    last_login_at = models.DateTimeField(
        _("last login at"),
        null=True,
        blank=True,
        help_text=_("Timestamp of user's most recent successful login."),
    )

    # ── Notification Preferences ──────────────────────────────────────────────

    notify_email = models.BooleanField(
        _("email notifications"),
        default=True,
        help_text=_("Whether to send notification emails to this user."),
    )
    notify_sms = models.BooleanField(
        _("SMS notifications"),
        default=False,
        help_text=_("Whether to send SMS notifications to this user."),
    )

    # ── Manager & Auth Config ─────────────────────────────────────────────────

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active", "is_verified"]),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"

    @property
    def is_admin(self) -> bool:
        """True if the user holds ADMIN or SUPER_ADMIN role."""
        return self.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)

    @property
    def is_volunteer_or_above(self) -> bool:
        """True if the user can participate in campaign activities."""
        return self.role in (
            UserRole.VOLUNTEER,
            UserRole.PHOTOGRAPHER,
            UserRole.COORDINATOR,
            UserRole.ORGANIZER,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        )

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.full_name.split()[0] if self.full_name else self.email

    @property
    def unread_notifications_count(self) -> int:
        """Returns the number of unread notifications for this user."""
        return self.notifications.filter(is_read=False).count()


# ─── OTP Token ────────────────────────────────────────────────────────────────


class OTPPurpose(models.TextChoices):
    """Describes what the OTP is being used for."""

    PHONE_LOGIN = "PHONE_LOGIN", _("Phone Login")
    EMAIL_VERIFY = "EMAIL_VERIFY", _("Email Verification")
    PASSWORD_RESET = "PASSWORD_RESET", _("Password Reset")
    ADMIN_LOGIN = "ADMIN_LOGIN", _("Admin 2FA Login")


class OTPToken(models.Model):
    """
    Stores one-time passwords for phone login, email verification, and password reset.

    Tokens are short-lived (10 minutes by default) and single-use.
    A new token invalidates all previous tokens for the same user+purpose.

    Security:
        - OTP codes are 6 digits (generated via secrets module in the service layer).
        - Expired tokens are cleaned up by a Celery beat task.
        - Rate limiting is enforced at the view layer (max 5 OTP requests per hour).
    """

    class Meta:
        verbose_name = _("OTP token")
        verbose_name_plural = _("OTP tokens")
        indexes = [
            models.Index(fields=["user", "purpose", "is_used"]),
        ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otp_tokens",
        verbose_name=_("user"),
    )
    purpose = models.CharField(
        _("purpose"),
        max_length=20,
        choices=OTPPurpose.choices,
    )
    code = models.CharField(
        _("OTP code"),
        max_length=6,
        help_text=_("6-digit one-time password."),
    )
    is_used = models.BooleanField(
        _("is used"),
        default=False,
        help_text=_("True once this token has been successfully verified."),
    )
    expires_at = models.DateTimeField(
        _("expires at"),
        help_text=_("Token is invalid after this timestamp."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def __str__(self) -> str:
        return f"OTP({self.purpose}) for {self.user.email}"

    @property
    def is_expired(self) -> bool:
        """True if the token has passed its expiry timestamp."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """True if the token can still be used."""
        return not self.is_used and not self.is_expired


# ─── Security & Audit Models ──────────────────────────────────────────────────

class DeviceFingerprint(models.Model):
    """Tracks known devices for an admin to alert on unknown logins."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    ip_address = models.GenericIPAddressField(_("IP address"))
    user_agent = models.CharField(_("user agent"), max_length=255)
    last_login_at = models.DateTimeField(_("last login"), auto_now=True)
    is_trusted = models.BooleanField(_("is trusted"), default=True)

    class Meta:
        verbose_name = _("device fingerprint")
        verbose_name_plural = _("device fingerprints")
        unique_together = ("user", "ip_address", "user_agent")

    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class AdminAuditLog(models.Model):
    """Enterprise Audit Log for tracking all admin actions."""
    
    class ActionType(models.TextChoices):
        LOGIN = "LOGIN", _("Login")
        LOGOUT = "LOGOUT", _("Logout")
        CREATE = "CREATE", _("Create")
        UPDATE = "UPDATE", _("Update")
        DELETE = "DELETE", _("Delete")
        PUBLISH = "PUBLISH", _("Publish")
        OTP_FAILURE = "OTP_FAILURE", _("OTP Failure")
        PASSWORD_CHANGE = "PASSWORD_CHANGE", _("Password Change")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_logs")
    action = models.CharField(_("action"), max_length=50, choices=ActionType.choices)
    model_name = models.CharField(_("model name"), max_length=100, blank=True)
    object_id = models.CharField(_("object ID"), max_length=255, blank=True)
    details = models.TextField(_("details"), blank=True)
    
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.CharField(_("user agent"), max_length=255, blank=True)
    
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        verbose_name = _("audit log")
        verbose_name_plural = _("audit logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
