from datetime import datetime, timedelta

from django.db import transaction

from .models import Appointment
from .tasks import send_appointment_confirmation


DAY_ALIASES = {
    "0": 0,
    "mon": 0,
    "monday": 0,
    "1": 1,
    "tue": 1,
    "tuesday": 1,
    "2": 2,
    "wed": 2,
    "wednesday": 2,
    "3": 3,
    "thu": 3,
    "thursday": 3,
    "4": 4,
    "fri": 4,
    "friday": 4,
    "5": 5,
    "sat": 5,
    "saturday": 5,
    "6": 6,
    "sun": 6,
    "sunday": 6,
}


def parse_available_days(value):
    days = set()
    for item in (value or "").split(","):
        key = item.strip().lower()
        if key in DAY_ALIASES:
            days.add(DAY_ALIASES[key])
    return days


def get_available_slots(doctor, date):
    if not doctor.consult_start or not doctor.consult_end:
        return []

    available_days = parse_available_days(doctor.available_days)
    if available_days and date.weekday() not in available_days:
        return []

    booked_times = set(
        Appointment.objects.filter(doctor=doctor, date=date)
        .exclude(status=Appointment.CANCELLED)
        .values_list("time", flat=True)
    )
    slots = []
    current = datetime.combine(date, doctor.consult_start)
    end = datetime.combine(date, doctor.consult_end)
    while current < end:
        slot = current.time().replace(second=0, microsecond=0)
        if slot not in booked_times:
            slots.append(slot)
        current += timedelta(minutes=15)
    return slots


@transaction.atomic
def book_appointment(patient, doctor, date, time, type=Appointment.OPD, notes=""):
    token_no = (
        Appointment.objects.select_for_update()
        .filter(doctor=doctor, date=date)
        .exclude(status=Appointment.CANCELLED)
        .count()
        + 1
    )
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        date=date,
        time=time,
        type=type,
        token_no=token_no,
        notes=notes,
    )
    send_appointment_confirmation.delay(appointment.pk)
    return appointment


def cancel_appointment(appointment, reason=""):
    appointment.status = Appointment.CANCELLED
    if reason:
        appointment.notes = f"{appointment.notes}\nCancellation reason: {reason}".strip()
    appointment.save(update_fields=["status", "notes"])
    send_appointment_confirmation.delay(appointment.pk)
    return appointment
