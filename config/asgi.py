"""
ASGI Configuration
==================
Exposes the ASGI callable for async-capable servers (Uvicorn, Daphne).
Currently used for Django Channels support in the future.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_asgi_application()
