import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import UUIDSoftDeleteModel

class StudentSubmission(UUIDSoftDeleteModel):
    class CompetitionType(models.TextChoices):
        ESSAY = "ESSAY", _("Essay Writing")
        DRAWING = "DRAWING", _("Drawing Competition")
        SUSTAINABLE_PROJECT = "SUSTAINABLE_PROJECT", _("Sustainable Project Making")

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", _("Pending Approval")
        APPROVED = "APPROVED", _("Approved for Showcase")
        REJECTED = "REJECTED", _("Rejected")

    participation_id = models.CharField(
        _("participation ID"),
        max_length=50,
        unique=True,
        blank=True,
        db_index=True
    )
    competition_type = models.CharField(
        _("competition type"),
        max_length=30,
        choices=CompetitionType.choices,
    )
    student_name = models.CharField(_("student name"), max_length=255)
    parent_name = models.CharField(_("parent / guardian name"), max_length=255)
    guardian_mobile = models.CharField(_("guardian mobile number"), max_length=10, unique=True)
    school_name = models.CharField(_("school name"), max_length=255)
    grade = models.PositiveSmallIntegerField(_("grade / standard"))
    
    uploaded_file = models.FileField(
        _("uploaded work"),
        upload_to="student_portal/submissions/"
    )
    student_photo = models.ImageField(
        _("student photo"),
        upload_to="student_portal/photos/%Y/%m/",
        blank=True,
        null=True
    )
    
    consent = models.BooleanField(_("consent provided"), default=False)
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("student submission")
        verbose_name_plural = _("student submissions")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.participation_id:
            self.participation_id = f"GN-STU-2026-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student_name} - {self.participation_id}"


class StudentCertificate(UUIDSoftDeleteModel):
    submission = models.OneToOneField(
        StudentSubmission,
        on_delete=models.CASCADE,
        related_name="certificate",
        verbose_name=_("student submission")
    )
    certificate_png = models.FileField(
        _("certificate PNG"),
        upload_to="student_portal/certificates/png/%Y/%m/",
        blank=True, null=True
    )
    certificate_pdf = models.FileField(
        _("certificate PDF"),
        upload_to="student_portal/certificates/pdf/%Y/%m/",
        blank=True, null=True
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("student certificate")
        verbose_name_plural = _("student certificates")
        ordering = ["-issued_at"]

    def __str__(self) -> str:
        return f"Certificate for {self.submission.student_name}"


class StudentShowcase(UUIDSoftDeleteModel):
    submission = models.OneToOneField(
        StudentSubmission,
        on_delete=models.CASCADE,
        related_name="showcase",
        verbose_name=_("approved submission")
    )
    featured = models.BooleanField(_("featured entry"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("student showcase entry")
        verbose_name_plural = _("student showcase entries")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Showcase: {self.submission.student_name}"
