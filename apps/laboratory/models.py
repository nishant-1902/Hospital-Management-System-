from django.conf import settings
from django.db import models


class LabTest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=50, db_index=True)
    normal_range = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=30, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ["name"]
        verbose_name = "lab test"
        verbose_name_plural = "lab tests"


class LabOrder(models.Model):
    ORDERED = "ORDERED"
    SAMPLE_COLLECTED = "SAMPLE_COLLECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (ORDERED, "Ordered"),
        (SAMPLE_COLLECTED, "Sample Collected"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    STAT = "STAT"

    PRIORITY_CHOICES = [
        (ROUTINE, "Routine"),
        (URGENT, "Urgent"),
        (STAT, "Stat"),
    ]

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT)
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT)
    record = models.ForeignKey("emr.MedicalRecord", null=True, blank=True, on_delete=models.SET_NULL)
    tests = models.ManyToManyField(LabTest, through="LabOrderItem")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ORDERED)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=ROUTINE)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lab order #{self.pk} - {self.patient}"

    class Meta:
        ordering = ["-ordered_at"]
        verbose_name = "lab order"
        verbose_name_plural = "lab orders"


class LabOrderItem(models.Model):
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE)
    test = models.ForeignKey(LabTest, on_delete=models.PROTECT)
    result = models.TextField(blank=True)
    flag = models.CharField(max_length=10, blank=True)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order} - {self.test}"

    class Meta:
        ordering = ["order", "test"]
        verbose_name = "lab order item"
        verbose_name_plural = "lab order items"
        constraints = [
            models.UniqueConstraint(fields=["order", "test"], name="unique_test_per_lab_order"),
        ]
