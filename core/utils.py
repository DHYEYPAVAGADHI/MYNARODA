"""
Core Utilities
===============
Pure utility functions with no side effects and no external dependencies.

Rules:
    - Every function solves exactly one problem.
    - No database access in this module.
    - No business logic in this module.
    - All functions must be thoroughly typed.
"""

import re
import uuid
from datetime import date

from django.utils.text import slugify as django_slugify


def generate_unique_slug(base_text: str, model_class, slug_field: str = "slug") -> str:
    """
    Generate a URL-safe slug from `base_text`, ensuring uniqueness
    against the given model class by appending a short UUID suffix if needed.

    Args:
        base_text: The source string to slugify (e.g. an event title).
        model_class: The Django model to check uniqueness against.
        slug_field: The name of the slug field on the model.

    Returns:
        A unique slug string.
    """
    base_slug = django_slugify(base_text)

    if not model_class.objects.filter(**{slug_field: base_slug}).exists():
        return base_slug

    # Append a 6-character UUID suffix for uniqueness
    unique_suffix = str(uuid.uuid4()).replace("-", "")[:6]
    return f"{base_slug}-{unique_suffix}"


def normalise_indian_phone(phone: str) -> str:
    """
    Normalise any valid Indian phone number to E.164 format: +91XXXXXXXXXX.

    Args:
        phone: A phone number in any accepted format.

    Returns:
        E.164 formatted phone number.

    Example:
        >>> normalise_indian_phone("9876543210")
        "+919876543210"
        >>> normalise_indian_phone("+91 98765 43210")
        "+919876543210"
    """
    cleaned = re.sub(r"[\s\-]", "", phone)
    # Remove leading 0, 91, or +91
    bare = re.sub(r"^(\+91|91|0)", "", cleaned)
    return f"+91{bare}"


def days_until_independence_day(target_year: int = 2027) -> int:
    """
    Calculate the number of days remaining until India's Independence Day
    in the given year (default: 2027, the 80th anniversary).

    Returns:
        Number of days (0 if today is the target date, negative if past).
    """
    target = date(target_year, 8, 15)
    today = date.today()
    return (target - today).days


def days_since_independence(from_year: int = 1947) -> int:
    """
    Calculate the number of days since India's first Independence Day.

    Returns:
        Integer count of days.
    """
    independence_day = date(from_year, 8, 15)
    return (date.today() - independence_day).days


def calculate_campaign_progress(trees_planted: int, goal: int = 28_855) -> float:
    """
    Calculate the campaign's percentage progress toward the tree planting goal.

    Returns:
        Float percentage clamped to [0.0, 100.0].
    """
    if goal <= 0:
        return 0.0
    progress = (trees_planted / goal) * 100
    return round(min(progress, 100.0), 2)


def truncate_text(text: str, max_length: int = 150, suffix: str = "…") -> str:
    """
    Truncate text to `max_length` characters, appending `suffix` if truncated.
    Word boundaries are respected to avoid cutting mid-word.

    Args:
        text: The source string.
        max_length: Maximum character length of the output (including suffix).
        suffix: The ellipsis string to append.

    Returns:
        Truncated string.
    """
    if len(text) <= max_length:
        return text

    truncated = text[: max_length - len(suffix)]
    # Walk back to the last space to avoid cutting mid-word
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + suffix
