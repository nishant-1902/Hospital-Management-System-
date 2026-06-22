from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.authentication.models import AuditLog

from .models import Patient


@receiver(post_save, sender=Patient)
def write_patient_audit_log(sender, instance, created, **kwargs):
    AuditLog.objects.create(
        user=None,
        action=AuditLog.CREATE if created else AuditLog.UPDATE,
        table_name="patients_patient",
        record_id=instance.pk,
        details=f"Patient {instance.pid} ({instance.name}) {'created' if created else 'updated'}.",
    )
