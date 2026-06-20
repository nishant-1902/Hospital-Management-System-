from django.contrib import admin

from .models import Attendance, LeaveRequest, Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("name", "designation", "department", "shift", "phone", "join_date", "is_active")
    list_filter = ("designation", "department", "shift", "is_active", "join_date")
    search_fields = ("name", "designation", "phone", "user__email")
    date_hierarchy = "join_date"


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("staff", "date", "check_in", "check_out", "status")
    list_filter = ("status", "date")
    search_fields = ("staff__name", "staff__user__email")
    date_hierarchy = "date"


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("staff", "from_date", "to_date", "status", "approved_by")
    list_filter = ("status", "from_date", "to_date")
    search_fields = ("staff__name", "staff__user__email", "reason", "approved_by__email")
    date_hierarchy = "from_date"
