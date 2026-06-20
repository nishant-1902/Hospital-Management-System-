from django.contrib import admin

from .models import Medicine, PharmacyStock, Prescription


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "generic_name", "category", "quantity", "unit", "reorder_level", "expiry_date", "price", "is_active")
    list_filter = ("category", "is_active", "expiry_date")
    search_fields = ("name", "generic_name", "unit")
    date_hierarchy = "expiry_date"


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("record", "medicine", "dosage", "frequency", "duration_days", "is_dispensed", "dispensed_at", "dispensed_by")
    list_filter = ("is_dispensed", "dispensed_at", "medicine")
    search_fields = ("record__patient__pid", "record__patient__name", "medicine__name", "dosage", "frequency")
    date_hierarchy = "dispensed_at"


@admin.register(PharmacyStock)
class PharmacyStockAdmin(admin.ModelAdmin):
    list_display = ("medicine", "batch_no", "quantity", "expiry_date", "received_at")
    list_filter = ("expiry_date", "received_at")
    search_fields = ("medicine__name", "medicine__generic_name", "batch_no")
    date_hierarchy = "received_at"
