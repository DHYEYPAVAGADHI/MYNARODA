from datetime import date

from django.db import transaction


def generate_tree_number():
    """
    Generate a unique sequential tree number in GNCN/YYYY/NNNNN format.
    Uses a DB-level lock to prevent duplicate IDs under concurrent submissions.
    """
    from apps.volunteers.models import PledgeRegistration

    year = date.today().year
    prefix = f"GNCN/{year}/"

    with transaction.atomic():
        existing = (
            PledgeRegistration.objects.select_for_update()
            .filter(tree_number__startswith=prefix)
            .order_by("-tree_number")
            .values_list("tree_number", flat=True)
            .first()
        )
        if existing:
            try:
                last_seq = int(existing.split("/")[-1])
            except (ValueError, IndexError):
                last_seq = 0
        else:
            last_seq = 0

        next_seq = last_seq + 1
        return f"{prefix}{next_seq:05d}"


def generate_certificate_id():
    """
    Generate a unique sequential certificate number in CERT/YYYY/NNNNN format.
    Uses a DB-level lock to prevent duplicate IDs under concurrent submissions.
    """
    from apps.volunteers.models import PledgeRegistration

    year = date.today().year
    prefix = f"CERT/{year}/"

    with transaction.atomic():
        existing = (
            PledgeRegistration.objects.select_for_update()
            .filter(certificate_id__startswith=prefix)
            .order_by("-certificate_id")
            .values_list("certificate_id", flat=True)
            .first()
        )
        if existing:
            try:
                last_seq = int(existing.split("/")[-1])
            except (ValueError, IndexError):
                last_seq = 0
        else:
            last_seq = 0

        next_seq = last_seq + 1
        return f"{prefix}{next_seq:05d}"


def assign_freedom_fighter_name(sequence_number):
    """
    Deterministically assigns a freedom fighter name based on a certificate's
    1-based sequence number: certificate #1 gets the 1st name in the pool
    (insertion order), #2 gets the 2nd, and so on. Once the pool is exhausted
    it cycles back to the 1st name and repeats.

    `sequence_number` should be the numeric suffix of the tree number
    (already generated under a DB lock), so this stays deterministic and
    race-free without any additional locking here.
    """
    from apps.volunteers.models import FreedomFighterName

    names = list(
        FreedomFighterName.objects.filter(is_active=True).order_by("id")
    )
    if not names:
        return None

    index = (sequence_number - 1) % len(names)
    return names[index]
