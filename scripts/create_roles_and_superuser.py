from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.color import no_style
from django.db import connection

User = get_user_model()

def run():
    print("Creating superuser...")
    email = "prathampriority@mynaroda.in"
    password = "Nikunj@1432"
    
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email=email, password=password)
        print(f"Superuser {email} created successfully.")
    else:
        print(f"Superuser {email} already exists.")

    print("Creating RBAC Groups...")
    groups = [
        "Admin",
        "Content Manager",
        "Gallery Manager",
        "Certificate Manager",
        "Volunteer Manager",
        "Event Manager",
        "Viewer"
    ]
    
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)
    
    print("Groups created successfully.")

if __name__ == '__main__':
    run()
