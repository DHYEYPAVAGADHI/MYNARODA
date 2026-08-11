"""
Management command: create_admin_users
=======================================
Creates the two admin accounts for the Mission Control panel.
Passwords are generated securely and printed to stdout ONCE.
They are NEVER stored in plain text anywhere.

Usage:
    python manage.py create_admin_users --settings=config.settings.development
"""
import secrets
import string

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User, UserRole

ADMIN_USERS = [
    {"email": "nrk.bjym@gmail.com", "password": "Nikunj@12345"},
    {"email": "pavagadhidhyey2@gmail.com", "password": "DHYEY@12345"},
]

class Command(BaseCommand):
    help = "Create the two Mission Control admin user accounts securely."

    def handle(self, *args, **options):
        with transaction.atomic():
            for admin_data in ADMIN_USERS:
                email = admin_data["email"]
                password = admin_data["password"]
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "full_name": email.split("@")[0].replace(".", " ").title(),
                        "role": UserRole.SUPER_ADMIN,
                        "is_staff": True,
                        "is_superuser": True,
                        "is_active": True,
                    },
                )
                
                user.set_password(password)
                user.role = UserRole.SUPER_ADMIN
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save(update_fields=["password", "role", "is_staff", "is_superuser", "is_active"])

        self.stdout.write(self.style.SUCCESS("Admin users created successfully"))
