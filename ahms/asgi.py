"""ASGI config for AHMS."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ahms.settings.development")

application = get_asgi_application()
