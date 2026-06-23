from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import LabOrderItem


@shared_task
def notify_critical_result(lab_order_item_id):
    item = (
        LabOrderItem.objects.select_related("order__patient", "order__doctor__user", "test")
        .filter(pk=lab_order_item_id)
        .first()
    )
    if not item:
        return False

    doctor_user = item.order.doctor.user
    if not doctor_user.email:
        return False

    subject = f"CRITICAL lab result: {item.test.name}"
    message = (
        f"Patient: {item.order.patient.name} ({item.order.patient.pid})\n"
        f"Test: {item.test.name} ({item.test.code})\n"
        f"Result: {item.result} {item.test.unit}\n"
        f"Flag: {item.flag}\n"
        f"Lab order: #{item.order_id}"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [doctor_user.email], fail_silently=False)
    return True
