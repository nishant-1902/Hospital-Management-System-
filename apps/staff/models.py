from django.conf import settings
from django.db import models


class Staff(models.Model):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"
    ROTATING = "ROTATING"

    SHIFT_CHOICES = [
        (MORNING, "Morning"),
        (AFTERNOON, "Afternoon"),
        (NIGHT, "Night"),
        (ROTATING, "Rotating"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=50)
    department = models.ForeignKey("doctors.Department", on_delete=models.SET_NULL, null=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    join_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.designation}"

    class Meta:
        ordering = ["name"]
        verbose_name = "staff"
        verbose_name_plural = "staff"


class Attendance(models.Model):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LEAVE = "LEAVE"

    STATUS_CHOICES = [
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
        (HALF_DAY, "Half Day"),
        (LEAVE, "Leave"),
    ]

    staff = models.ForeignKey(Staff, related_name="attendance", on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.staff} - {self.date} - {self.status}"

    class Meta:
        ordering = ["-date", "staff"]
        verbose_name = "attendance"
        verbose_name_plural = "attendance"
        constraints = [
            models.UniqueConstraint(fields=["staff", "date"], name="unique_staff_attendance_date"),
        ]


class LeaveRequest(models.Model):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.staff} leave from {self.from_date} to {self.to_date}"

    class Meta:
        ordering = ["-from_date"]
        verbose_name = "leave request"
        verbose_name_plural = "leave requests"
