from rest_framework import serializers

from .models import LabOrder, LabOrderItem, LabTest


class LabTestSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = LabTest
        fields = ["id", "name", "code", "category", "normal_range", "unit", "price", "label"]

    def get_label(self, obj):
        unit = f" ({obj.unit})" if obj.unit else ""
        return f"{obj.code} - {obj.name}{unit}"


class LabOrderItemSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source="test.name", read_only=True)
    test_code = serializers.CharField(source="test.code", read_only=True)
    unit = serializers.CharField(source="test.unit", read_only=True)

    class Meta:
        model = LabOrderItem
        fields = ["id", "test", "test_name", "test_code", "result", "flag", "verified", "completed_at", "unit"]
        read_only_fields = ["id", "test_name", "test_code", "flag", "completed_at", "unit"]


class LabOrderSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    items = LabOrderItemSerializer(source="laborderitem_set", many=True, read_only=True)
    test_ids = serializers.PrimaryKeyRelatedField(
        source="tests",
        queryset=LabTest.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = LabOrder
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "record",
            "status",
            "priority",
            "ordered_at",
            "test_ids",
            "items",
        ]
        read_only_fields = ["id", "patient_name", "doctor_name", "ordered_at", "items"]

    def create(self, validated_data):
        tests = validated_data.pop("tests", [])
        order = LabOrder.objects.create(**validated_data)
        for test in tests:
            LabOrderItem.objects.create(order=order, test=test)
        return order

    def update(self, instance, validated_data):
        tests = validated_data.pop("tests", None)
        instance = super().update(instance, validated_data)
        if tests is not None:
            existing = set(instance.laborderitem_set.values_list("test_id", flat=True))
            desired = {test.pk for test in tests}
            instance.laborderitem_set.filter(test_id__in=existing - desired).delete()
            for test in tests:
                if test.pk not in existing:
                    LabOrderItem.objects.create(order=instance, test=test)
        return instance
