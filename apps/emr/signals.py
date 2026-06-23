import json

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.authentication.models import AuditLog
from apps.pharmacy.models import Prescription

from .models import EMRHistory, MedicalRecord


@receiver(post_save, sender=MedicalRecord)
def create_emr_history_snapshot(sender, instance, **kwargs):
    snapshot = {
        "id": instance.pk,
        "appointment_id": instance.appointment_id,
        "patient_id": instance.patient_id,
        "doctor_id": instance.doctor_id,
        "diagnosis": instance.diagnosis,
        "icd10_code": instance.icd10_code,
        "treatment": instance.treatment,
        "soap_notes": instance.soap_notes,
        "created_at": instance.created_at.isoformat() if instance.created_at else None,
        "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
    }
    EMRHistory.objects.create(record=instance, changed_by=None, snapshot=json.dumps(snapshot))


@receiver(pre_save, sender=Prescription)
def remember_prescription_dispense_state(sender, instance, **kwargs):
    if instance.pk:
        instance._was_dispensed = Prescription.objects.filter(pk=instance.pk).values_list("is_dispensed", flat=True).first()
    else:
        instance._was_dispensed = False


@receiver(post_save, sender=Prescription)
def audit_prescription_dispensed(sender, instance, **kwargs):
    if instance.is_dispensed and not getattr(instance, "_was_dispensed", False):
        AuditLog.objects.create(
            user=instance.dispensed_by,
            action=AuditLog.UPDATE,
            table_name="pharmacy_prescription",
            record_id=instance.pk,
            details=f"Prescription #{instance.pk} dispensed for {instance.record.patient}.",
        )
