from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"
    RECEPTIONIST = "RECEPTIONIST"
    PHARMACIST = "PHARMACIST"
    LAB_TECH = "LAB_TECH"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (DOCTOR, "Doctor"),
        (PATIENT, "Patient"),
        (RECEPTIONIST, "Receptionist"),
        (PHARMACIST, "Pharmacist"),
        (LAB_TECH, "Lab Technician"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    class Meta:
        ordering = ["email"]
        verbose_name = "user"
        verbose_name_plural = "users"


class AuditLog(models.Model):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS_DENIED = "ACCESS_DENIED"

    ACTION_CHOICES = [
        (CREATE, "Create"),
        (UPDATE, "Update"),
        (DELETE, "Delete"),
        (LOGIN, "Login"),
        (LOGOUT, "Logout"),
        (ACCESS_DENIED, "Access Denied"),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    table_name = models.CharField(max_length=50, blank=True)
    record_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        actor = self.user.email if self.user else "System"
        return f"{actor} - {self.action} - {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "audit log"
        verbose_name_plural = "audit logs"
        indexes = [
            models.Index(fields=["user"], name="audit_user_idx"),
            models.Index(fields=["action"], name="audit_action_idx"),
            models.Index(fields=["timestamp"], name="audit_timestamp_idx"),
        ]
