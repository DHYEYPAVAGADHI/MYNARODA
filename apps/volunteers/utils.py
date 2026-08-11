import random
from datetime import date

from django.db import transaction


def generate_certificate_id():
    return f'GNCN/{date.today().year}/{random.randint(1, 99999):05d}'


def generate_tree_number(pledge_id):
    return f'GN-TREE-{date.today().year}-{pledge_id:05d}'


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
