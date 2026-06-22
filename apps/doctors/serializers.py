from rest_framework import serializers

from .models import Department, Doctor


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "location", "created_at"]
        read_only_fields = ["id", "created_at"]


class DoctorSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "user",
            "email",
            "name",
            "specialization",
            "department",
            "department_name",
            "qualification",
            "experience_yrs",
            "available_days",
            "consult_start",
            "consult_end",
            "is_active",
        ]
        read_only_fields = ["id", "user", "email", "department_name"]
