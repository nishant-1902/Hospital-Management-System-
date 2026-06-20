from django.contrib import admin

from .models import Department, Doctor


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "location")
    date_hierarchy = "created_at"


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialization", "department", "qualification", "experience_yrs", "is_active")
    list_filter = ("department", "specialization", "is_active")
    search_fields = ("name", "specialization", "qualification", "user__email", "user__phone")
