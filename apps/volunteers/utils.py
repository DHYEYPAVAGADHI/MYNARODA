import random
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
    Generate a unique sequential certificate number in NC/YYYY/NNNNN format.
    Uses a DB-level lock to prevent duplicate IDs under concurrent submissions.
    """
    from apps.volunteers.models import PledgeRegistration

    year = date.today().year
    prefix = f"NC/{year}/"

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


def assign_freedom_fighter_name():
    """
    Randomly assigns an unused freedom fighter name from the pool.
    Once every active name has been used once, the whole pool resets
    and names start repeating in a new random order.
    Row-locked so two simultaneous pledges never race for the same name.
    """
    from apps.volunteers.models import FreedomFighterName

    with transaction.atomic():
        available = list(
            FreedomFighterName.objects.select_for_update()
            .filter(is_active=True, used_in_current_cycle=False)
        )

        if not available:
            FreedomFighterName.objects.filter(is_active=True).update(used_in_current_cycle=False)
            available = list(
                FreedomFighterName.objects.select_for_update()
                .filter(is_active=True, used_in_current_cycle=False)
            )

        if not available:
            return None

        chosen = random.choice(available)
        chosen.used_in_current_cycle = True
        chosen.save(update_fields=['used_in_current_cycle'])
        return chosen
