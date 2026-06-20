from django.conf import settings
from django.db import models


class MedicalRecord(models.Model):
    appointment = models.OneToOneField("appointments.Appointment", on_delete=models.PROTECT)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT)
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT)
    diagnosis = models.TextField()
    icd10_code = models.CharField(max_length=20, blank=True)
    treatment = models.TextField()
    soap_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record #{self.pk} - {self.patient}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "medical record"
        verbose_name_plural = "medical records"


class EMRAttachment(models.Model):
    record = models.ForeignKey(MedicalRecord, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="emr_attachments/")
    label = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label or f"Attachment #{self.pk}"

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "EMR attachment"
        verbose_name_plural = "EMR attachments"


class EMRHistory(models.Model):
    record = models.ForeignKey(MedicalRecord, related_name="history", on_delete=models.CASCADE)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    snapshot = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History #{self.pk} for {self.record}"

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "EMR history"
        verbose_name_plural = "EMR history"
