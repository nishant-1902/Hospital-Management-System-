from django.contrib import admin

from .models import Bill, BillItem, Payment


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "appointment", "net_amount", "paid_amount", "payment_status", "payment_method", "created_at")
    list_filter = ("payment_status", "payment_method", "created_at")
    search_fields = ("patient__pid", "patient__name", "insurance_claim", "notes")
    date_hierarchy = "created_at"


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ("bill", "item_type", "description", "quantity", "unit_price", "total_price")
    list_filter = ("item_type",)
    search_fields = ("bill__patient__pid", "bill__patient__name", "description")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("bill", "amount", "method", "reference", "paid_at", "received_by")
    list_filter = ("method", "paid_at")
    search_fields = ("bill__patient__pid", "bill__patient__name", "reference", "received_by__email")
    date_hierarchy = "paid_at"
