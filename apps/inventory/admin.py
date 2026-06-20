from django.contrib import admin

from .models import InventoryItem, PurchaseOrder, PurchaseOrderItem, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact", "email")
    list_filter = ("name",)
    search_fields = ("name", "contact", "email", "address")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity", "unit", "reorder_level", "unit_cost", "supplier", "last_restocked")
    list_filter = ("category", "supplier", "last_restocked")
    search_fields = ("name", "unit", "supplier__name")
    date_hierarchy = "last_restocked"


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "status", "created_by", "created_at", "received_at")
    list_filter = ("status", "supplier", "created_at", "received_at")
    search_fields = ("supplier__name", "created_by__email", "notes")
    date_hierarchy = "created_at"


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "item", "quantity", "unit_price")
    list_filter = ("item",)
    search_fields = ("order__supplier__name", "item__name")
