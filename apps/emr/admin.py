from django.contrib import admin

from .models import EMRAttachment, EMRHistory, MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "appointment", "icd10_code", "created_at", "updated_at")
    list_filter = ("doctor", "created_at", "updated_at")
    search_fields = ("patient__pid", "patient__name", "doctor__name", "diagnosis", "icd10_code", "treatment")
    date_hierarchy = "created_at"


@admin.register(EMRAttachment)
class EMRAttachmentAdmin(admin.ModelAdmin):
    list_display = ("record", "label", "file", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("record__patient__pid", "record__patient__name", "label", "file")
    date_hierarchy = "uploaded_at"


@admin.register(EMRHistory)
class EMRHistoryAdmin(admin.ModelAdmin):
    list_display = ("record", "changed_by", "changed_at")
    list_filter = ("changed_at",)
    search_fields = ("record__patient__pid", "record__patient__name", "changed_by__email", "snapshot")
    date_hierarchy = "changed_at"
