from django.contrib import admin

from .models import Admission, Bed, Ward


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ("name", "ward_type", "floor", "capacity")
    list_filter = ("ward_type", "floor")
    search_fields = ("name", "floor")


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("ward", "bed_number", "status", "patient", "admitted_at")
    list_filter = ("status", "ward", "admitted_at")
    search_fields = ("ward__name", "bed_number", "patient__pid", "patient__name")
    date_hierarchy = "admitted_at"


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ("patient", "bed", "admitted_by", "admission_date", "discharge_date", "is_active")
    list_filter = ("is_active", "admission_date", "discharge_date", "bed__ward")
    search_fields = ("patient__pid", "patient__name", "bed__bed_number", "admitted_by__email", "discharge_notes")
    date_hierarchy = "admission_date"
