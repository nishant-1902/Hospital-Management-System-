from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Appointment


@shared_task
def send_appointment_confirmation(appointment_id):
    appointment = (
        Appointment.objects.select_related("patient", "doctor", "patient__user")
        .filter(pk=appointment_id)
        .first()
    )
    if not appointment:
        return "appointment-not-found"

    recipient = getattr(getattr(appointment.patient, "user", None), "email", "")
    if not recipient:
        return "patient-email-missing"

    subject = f"AHMS appointment {appointment.get_status_display()}"
    message = (
        f"Dear {appointment.patient.name},\n\n"
        f"Your appointment with {appointment.doctor} is {appointment.get_status_display().lower()}.\n"
        f"Date: {appointment.date:%d %b %Y}\n"
        f"Time: {appointment.time:%I:%M %p}\n"
        f"Token: {appointment.token_no or '-'}\n\n"
        "AHMS"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)
    return "sent"


@shared_task
def send_appointment_reminder(appointment_id):
    appointment = (
        Appointment.objects.select_related("patient", "doctor", "patient__user")
        .filter(pk=appointment_id)
        .first()
    )
    if not appointment or appointment.status == Appointment.CANCELLED:
        return "skipped"

    recipient = getattr(getattr(appointment.patient, "user", None), "email", "")
    if not recipient:
        return "patient-email-missing"

    starts_at = datetime.combine(appointment.date, appointment.time)
    subject = "AHMS appointment reminder"
    message = (
        f"Dear {appointment.patient.name},\n\n"
        f"This is a reminder for your appointment with {appointment.doctor} at {starts_at:%I:%M %p}.\n"
        f"Token: {appointment.token_no or '-'}\n\n"
        "AHMS"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)
    return "sent"
