from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "date",
            "time",
            "status",
            "type",
            "notes",
            "token_no",
            "created_at",
        ]
        read_only_fields = ["id", "token_no", "created_at", "patient_name", "doctor_name"]
