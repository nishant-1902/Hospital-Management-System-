from django.contrib import admin

from .models import LabOrder, LabOrderItem, LabTest


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "normal_range", "unit", "price")
    list_filter = ("category",)
    search_fields = ("code", "name", "category")


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "status", "priority", "ordered_at")
    list_filter = ("status", "priority", "ordered_at", "doctor")
    search_fields = ("patient__pid", "patient__name", "doctor__name")
    date_hierarchy = "ordered_at"


@admin.register(LabOrderItem)
class LabOrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "test", "flag", "verified", "verified_by", "completed_at")
    list_filter = ("verified", "flag", "completed_at")
    search_fields = ("order__patient__pid", "order__patient__name", "test__code", "test__name", "result")
    date_hierarchy = "completed_at"
