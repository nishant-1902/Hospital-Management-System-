from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("pid", "name", "gender", "dob", "phone", "blood_group", "is_active", "created_at")
    list_filter = ("gender", "blood_group", "is_active", "created_at")
    search_fields = ("pid", "name", "phone", "address", "user__email")
    date_hierarchy = "created_at"
    readonly_fields = ("pid", "created_at", "updated_at")
