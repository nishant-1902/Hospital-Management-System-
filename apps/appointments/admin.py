from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "date", "time", "status", "type", "token_no", "created_at")
    list_filter = ("status", "type", "date", "doctor")
    search_fields = ("patient__pid", "patient__name", "doctor__name", "notes")
    date_hierarchy = "date"
