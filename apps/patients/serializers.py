from datetime import date

from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "patient_id",
            "user",
            "pid",
            "name",
            "gender",
            "dob",
            "phone",
            "address",
            "blood_group",
            "photo",
            "id_document",
            "created_at",
            "updated_at",
            "is_active",
            "age",
        ]
        read_only_fields = ["patient_id", "pid", "created_at", "updated_at", "age"]

    def get_age(self, obj):
        if not obj.dob:
            return None
        today = date.today()
        return today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))


class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["pid", "name", "phone", "gender", "dob"]
