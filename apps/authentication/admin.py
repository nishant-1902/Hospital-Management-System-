from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuditLog, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Hospital Access", {"fields": ("role", "phone", "profile_photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Hospital Access", {"fields": ("email", "role", "phone", "profile_photo")}),
    )
    list_display = ("email", "username", "first_name", "last_name", "role", "phone", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    ordering = ("email",)
    date_hierarchy = "date_joined"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "table_name", "record_id", "ip_address")
    list_filter = ("action", "timestamp")
    search_fields = ("user__email", "user__username", "table_name", "record_id", "details", "ip_address")
    date_hierarchy = "timestamp"
    readonly_fields = ("timestamp",)
