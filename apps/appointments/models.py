from django.db import models


class Appointment(models.Model):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (SCHEDULED, "Scheduled"),
        (CONFIRMED, "Confirmed"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    OPD = "OPD"
    IPD = "IPD"
    EMERGENCY = "EMERGENCY"
    TELECONSULTATION = "TELECONSULTATION"

    TYPE_CHOICES = [
        (OPD, "OPD"),
        (IPD, "IPD"),
        (EMERGENCY, "Emergency"),
        (TELECONSULTATION, "Teleconsultation"),
    ]

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT)
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SCHEDULED)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=OPD)
    notes = models.TextField(blank=True)
    token_no = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} at {self.time}"

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = "appointment"
        verbose_name_plural = "appointments"
        constraints = [
            models.UniqueConstraint(fields=["doctor", "date", "time"], name="unique_doctor_appointment_slot"),
        ]
