from django.conf import settings
from django.db import models


class Medicine(models.Model):
    TABLET = "TABLET"
    SYRUP = "SYRUP"
    INJECTION = "INJECTION"
    OINTMENT = "OINTMENT"
    DROPS = "DROPS"
    OTHER = "OTHER"

    CATEGORY_CHOICES = [
        (TABLET, "Tablet"),
        (SYRUP, "Syrup"),
        (INJECTION, "Injection"),
        (OINTMENT, "Ointment"),
        (DROPS, "Drops"),
        (OTHER, "Other"),
    ]

    name = models.CharField(max_length=100)
    generic_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20)
    reorder_level = models.PositiveIntegerField(default=10)
    expiry_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.generic_name})"

    class Meta:
        ordering = ["name"]
        verbose_name = "medicine"
        verbose_name_plural = "medicines"


class Prescription(models.Model):
    record = models.ForeignKey("emr.MedicalRecord", related_name="prescriptions", on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    duration_days = models.PositiveSmallIntegerField()
    instructions = models.TextField(blank=True)
    is_dispensed = models.BooleanField(default=False)
    dispensed_at = models.DateTimeField(null=True, blank=True)
    dispensed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.medicine} for {self.record.patient}"

    class Meta:
        ordering = ["record", "medicine"]
        verbose_name = "prescription"
        verbose_name_plural = "prescriptions"


class PharmacyStock(models.Model):
    medicine = models.ForeignKey(Medicine, related_name="batches", on_delete=models.CASCADE)
    batch_no = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine} - {self.batch_no}"

    class Meta:
        ordering = ["expiry_date", "medicine"]
        verbose_name = "pharmacy stock"
        verbose_name_plural = "pharmacy stock"
        constraints = [
            models.UniqueConstraint(fields=["medicine", "batch_no"], name="unique_medicine_batch"),
        ]
