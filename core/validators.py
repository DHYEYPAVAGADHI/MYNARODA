"""
Core Validators
================
Shared, reusable validators for use in models and serializers.

Each validator is a standalone callable that raises ValidationError
(from django.core.exceptions) on failure.

Usage in a model field:
    phone = models.CharField(validators=[validate_indian_phone])

Usage in a serializer field:
    phone = serializers.CharField(validators=[validate_indian_phone])
"""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_indian_phone(value: str) -> None:
    """
    Validates that a phone number matches the Indian mobile format.

    Valid formats: +91XXXXXXXXXX, 91XXXXXXXXXX, 0XXXXXXXXXX, XXXXXXXXXX
    All formats are normalised to E.164 (+91XXXXXXXXXX) at save time.
    """
    # Strip spaces and hyphens
    cleaned = re.sub(r"[\s\-]", "", value)

    # Accept +91, 91, 0 prefixes or bare 10-digit numbers
    pattern = r"^(\+91|91|0)?[6-9]\d{9}$"

    if not re.fullmatch(pattern, cleaned):
        raise ValidationError(
            _("Enter a valid Indian mobile number (e.g. +91 98765 43210)."),
            code="invalid_phone",
        )


def validate_image_file_size(value) -> None:
    """
    Validates that an uploaded image does not exceed 10 MB.
    Cloudinary will further compress images, but we reject excessively large files
    at the validation layer to protect server resources.
    """
    max_size_mb = 10
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _(f"Image file size must not exceed {max_size_mb} MB."),
            code="file_too_large",
        )


def validate_latitude(value: float) -> None:
    """Validates that a latitude coordinate is within the valid range [-90, 90]."""
    if not (-90 <= value <= 90):
        raise ValidationError(
            _("Latitude must be between -90 and 90."),
            code="invalid_latitude",
        )


def validate_longitude(value: float) -> None:
    """Validates that a longitude coordinate is within the valid range [-180, 180]."""
    if not (-180 <= value <= 180):
        raise ValidationError(
            _("Longitude must be between -180 and 180."),
            code="invalid_longitude",
        )
