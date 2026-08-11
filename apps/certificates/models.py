import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import UUIDSoftDeleteModel

class Certificate(UUIDSoftDeleteModel):
    class CertificateType(models.TextChoices):
        VOLUNTEER = "VOLUNTEER", _("Volunteer Excellence")
        PLANTATION = "PLANTATION", _("Tree Plantation Certificate")
        EVENT = "EVENT", _("Event Participation")
        PARTICIPATION = "PARTICIPATION", _("General Campaign Participation")

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name=_("user"),
    )
    certificate_type = models.CharField(
        _("certificate type"),
        max_length=20,
        choices=CertificateType.choices,
        default=CertificateType.PARTICIPATION,
    )
    certificate_number = models.CharField(
        _("certificate number"),
        max_length=50,
        unique=True,
        blank=True,
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_certificates",
        verbose_name=_("event"),
    )
    tree = models.ForeignKey(
        "trees.Tree",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_certificates",
        verbose_name=_("tree"),
    )
    issued_at = models.DateTimeField(_("issued at"), auto_now_add=True)

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")
        ordering = ["-issued_at"]

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate a nice certificate number like GN-2027-XXXXXX
            self.certificate_number = f"GN-2027-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.get_certificate_type_display()} - {self.user.full_name} ({self.certificate_number})"
