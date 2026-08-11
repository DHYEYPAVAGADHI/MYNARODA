"""
Volunteers App — Models
=======================
Includes Pledge Registration for the public campaign.
"""
from datetime import date
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel
from core.validators import validate_indian_phone



class OrganizationType(models.TextChoices):
    GOVERNMENT = "GOVERNMENT", _("Government")
    PRIVATE = "PRIVATE", _("Private")
    NGO = "NGO", _("NGO")
    EDUCATIONAL = "EDUCATIONAL", _("Educational")
    CORPORATE = "CORPORATE", _("Corporate")
    VOLUNTEER_GROUP = "VOLUNTEER_GROUP", _("Volunteer Group")
    OTHERS = "OTHERS", _("Others")

class Organization(TimeStampedModel):
    name = models.CharField(_("organization name"), max_length=200, unique=True)
    org_type = models.CharField(_("organization type"), max_length=50, choices=OrganizationType.choices, default=OrganizationType.OTHERS)
    logo = models.ImageField(_("organization logo"), upload_to="organizations/", blank=True, null=True)
    is_active = models.BooleanField(_("is active"), default=True)
    sort_order = models.IntegerField(_("sort order"), default=0)

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        ordering = ["name"]

    def __str__(self):
        return self.name


class FreedomFighterName(TimeStampedModel):
    """
    Pool of freedom fighter names each dedicated tree is named after on the
    Tree Pledge Certificate. Assignment is random; once every name in the
    pool has been used once, the pool resets and names start repeating.
    """
    name = models.CharField(_("freedom fighter name"), max_length=150, unique=True)
    is_active = models.BooleanField(_("is active"), default=True)
    used_in_current_cycle = models.BooleanField(_("used in current cycle"), default=False)

    class Meta:
        verbose_name = _("freedom fighter name")
        verbose_name_plural = _("freedom fighter names")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class PledgeRegistration(TimeStampedModel):
    """
    Public registration from the homepage popup for Tree Plantation & Adoption Pledge.
    """
    class GenderChoices(models.TextChoices):
        MALE = "MALE", _("Male")
        FEMALE = "FEMALE", _("Female")
        OTHER = "OTHER", _("Other")
        PREFER_NOT_TO_SAY = "PREFER_NOT", _("Prefer Not to Say")

    # Personal Information
    full_name = models.CharField(_("full name"), max_length=150)
    mobile_number = models.CharField(
        _("mobile number"),
        max_length=15,
        validators=[validate_indian_phone],
    )
    email = models.EmailField(_("email address"), blank=True, default="")
    gender = models.CharField(
        _("gender"),
        max_length=20,
        choices=GenderChoices.choices,
    )
    date_of_birth = models.DateField(_("date of birth"))
    age = models.PositiveIntegerField(_("calculated age"), blank=True, null=True, editable=False)
    city = models.CharField(_("city"), max_length=100, default="Ahmedabad")
    pincode = models.CharField(_("pincode"), max_length=10, default="382330")

    # Associate Organization
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name=_("organization"))

    # Consent and Status
    agreed_to_pledge = models.BooleanField(_("agreed to pledge"), default=True)
    consent_accepted = models.BooleanField(_("consent accepted"), default=True)
    otp_verified = models.BooleanField(_("otp verified"), default=True)
    
    is_approved = models.BooleanField(_("is approved"), default=True)
    
    # Certificate Fields
    certificate_id = models.CharField(_("certificate id"), max_length=20, unique=True, blank=True, null=True)
    tree_number = models.CharField(_("tree number"), max_length=20, unique=True, blank=True, null=True)
    dedicated_to = models.ForeignKey(
        FreedomFighterName, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="dedicated_trees", verbose_name=_("dedicated to freedom fighter"),
    )
    certificate_image = models.ImageField(_("certificate image"), upload_to="certificates/images/", blank=True, null=True)
    certificate_pdf = models.FileField(_("certificate pdf"), upload_to="certificates/pdfs/", blank=True, null=True)
    
    # Analytics & Tracking Fields
    generated_at = models.DateTimeField(blank=True, null=True)
    whatsapp_sent = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    share_ig_count = models.PositiveIntegerField(default=0)
    share_wa_count = models.PositiveIntegerField(default=0)
    share_fb_count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    browser_info = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = _("pledge registration")
        verbose_name_plural = _("pledge registrations")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.certificate_id or 'Pending'}"

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            today = date.today()
            self.age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        super().save(*args, **kwargs)
