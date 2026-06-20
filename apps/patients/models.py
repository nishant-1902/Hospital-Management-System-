from django.conf import settings
from django.db import models
from django.utils import timezone


class Patient(models.Model):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    pid = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField()
    phone = models.CharField(max_length=15, db_index=True)
    address = models.TextField()
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    photo = models.ImageField(upload_to="patients/", blank=True, null=True)
    id_document = models.FileField(upload_to="patient_docs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pid:
            year = timezone.now().year
            last_patient = Patient.objects.filter(pid__startswith=f"AHMS-{year}-").order_by("-patient_id").first()
            next_number = 1
            if last_patient and last_patient.pid:
                next_number = int(last_patient.pid.rsplit("-", 1)[-1]) + 1
            self.pid = f"AHMS-{year}-{next_number:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pid} - {self.name}"

    class Meta:
        ordering = ["name"]
        verbose_name = "patient"
        verbose_name_plural = "patients"
