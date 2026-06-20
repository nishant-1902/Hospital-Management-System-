from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "department"
        verbose_name_plural = "departments"


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    qualification = models.CharField(max_length=200)
    experience_yrs = models.PositiveSmallIntegerField(default=0)
    available_days = models.CharField(max_length=200, blank=True)
    consult_start = models.TimeField(null=True, blank=True)
    consult_end = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

    class Meta:
        ordering = ["name"]
        verbose_name = "doctor"
        verbose_name_plural = "doctors"
