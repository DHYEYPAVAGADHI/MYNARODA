from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
import uuid

class CompetitionRegistration(TimeStampedModel):
    class ApprovalStatus(models.TextChoices):
        PENDING = "PENDING", _("Pending Review")
        APPROVED = "APPROVED", _("Approved")
        REJECTED = "REJECTED", _("Rejected")

    # Step 1: Organization
    organization_type = models.ForeignKey(
        'CompetitionOrganizationType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Organization Type")
    )
    organization_name = models.CharField(max_length=255, verbose_name=_("Organization Name"))
    registration_number = models.CharField(max_length=100, blank=True, verbose_name=_("Registration Number (optional)"))
    address = models.TextField(verbose_name=_("Full Address"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    pincode = models.CharField(max_length=20, verbose_name=_("Pincode"))
    
    # Conditional fields for Society
    homes_count = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Number of Homes in Society"))
    members_participating = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Members Participating"))

    # Step 2: Contact
    authorized_person_name = models.CharField(max_length=255, verbose_name=_("Authorized Person Name"))
    designation = models.CharField(max_length=100, blank=True, verbose_name=_("Designation"))
    mobile_number = models.CharField(max_length=20, verbose_name=_("Mobile Number"))
    whatsapp_number = models.CharField(max_length=20, verbose_name=_("WhatsApp Number"))
    alternate_number = models.CharField(max_length=20, blank=True, verbose_name=_("Another Contact Number"))
    email = models.EmailField(verbose_name=_("Email Address"))

    # Step 3: Sustainability
    solar_installed = models.BooleanField(default=False, verbose_name=_("Is Solar Panel Installed?"))
    solar_panels_count = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Number of Solar Panels"))
    rainwater_harvesting = models.BooleanField(default=False, verbose_name=_("Do you have Rainwater Harvesting?"))
    
    supporting_file = models.FileField(
        upload_to="competition/evidence/%Y/%m/",
        verbose_name=_("Supporting Evidence"),
        help_text=_("Upload Photos / Documents (JPG, PNG, PDF)")
    )

    # Status & Certificates
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        verbose_name=_("Approval Status")
    )
    registration_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name=_("Registration ID")
    )
    certificate_png = models.ImageField(upload_to='certificates/organizations/png/', blank=True, null=True)
    certificate_pdf = models.FileField(upload_to='certificates/organizations/pdf/', blank=True, null=True)
    certificate_generated = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Competition Registration")
        verbose_name_plural = _("Competition Registrations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization_name} ({self.registration_id})"

    def save(self, *args, **kwargs):
        if not self.registration_id:
            # We will assign ID after saving if we need PK, but since it's just a random ID we can generate it
            super().save(*args, **kwargs) # To get PK if needed, but wait, if it's an abstract ID
            self.registration_id = f"GN-COMP-2026-{self.pk:05d}"
            super().save(update_fields=['registration_id'])
        else:
            super().save(*args, **kwargs)

    @property
    def is_approved(self):
        return self.status == self.ApprovalStatus.APPROVED


class CompetitionOrganizationType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Organization Type Name"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    sort_order = models.IntegerField(default=0, verbose_name=_("Sort Order"))

    class Meta:
        verbose_name = _("Competition Organization Type")
        verbose_name_plural = _("Competition Organization Types")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name
