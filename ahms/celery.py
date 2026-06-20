"""Celery application for AHMS."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ahms.settings.development")

app = Celery("ahms")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
