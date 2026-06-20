from django.conf import settings
from django.db import models


class Ward(models.Model):
    GENERAL = "GENERAL"
    ICU = "ICU"
    NICU = "NICU"
    PRIVATE = "PRIVATE"
    SEMI_PRIVATE = "SEMI_PRIVATE"
    HDU = "HDU"

    WARD_TYPE_CHOICES = [
        (GENERAL, "General"),
        (ICU, "ICU"),
        (NICU, "NICU"),
        (PRIVATE, "Private"),
        (SEMI_PRIVATE, "Semi Private"),
        (HDU, "HDU"),
    ]

    name = models.CharField(max_length=100, unique=True)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPE_CHOICES)
    floor = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "ward"
        verbose_name_plural = "wards"


class Bed(models.Model):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"

    STATUS_CHOICES = [
        (AVAILABLE, "Available"),
        (OCCUPIED, "Occupied"),
        (MAINTENANCE, "Maintenance"),
        (RESERVED, "Reserved"),
    ]

    ward = models.ForeignKey(Ward, related_name="beds", on_delete=models.CASCADE)
    bed_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)
    patient = models.ForeignKey("patients.Patient", null=True, blank=True, on_delete=models.SET_NULL)
    admitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.ward} - Bed {self.bed_number}"

    class Meta:
        ordering = ["ward", "bed_number"]
        verbose_name = "bed"
        verbose_name_plural = "beds"
        constraints = [
            models.UniqueConstraint(fields=["ward", "bed_number"], name="unique_bed_per_ward"),
        ]


class Admission(models.Model):
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT)
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT)
    admitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="admissions", on_delete=models.PROTECT)
    admission_date = models.DateTimeField(auto_now_add=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    discharge_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient} admitted to {self.bed}"

    class Meta:
        ordering = ["-admission_date"]
        verbose_name = "admission"
        verbose_name_plural = "admissions"
