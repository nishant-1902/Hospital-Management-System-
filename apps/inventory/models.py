from django.conf import settings
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "supplier"
        verbose_name_plural = "suppliers"


class InventoryItem(models.Model):
    CONSUMABLE = "CONSUMABLE"
    EQUIPMENT = "EQUIPMENT"
    LINEN = "LINEN"
    CLEANING = "CLEANING"
    STATIONERY = "STATIONERY"
    OTHER = "OTHER"

    CATEGORY_CHOICES = [
        (CONSUMABLE, "Consumable"),
        (EQUIPMENT, "Equipment"),
        (LINEN, "Linen"),
        (CLEANING, "Cleaning"),
        (STATIONERY, "Stationery"),
        (OTHER, "Other"),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20)
    reorder_level = models.PositiveIntegerField(default=5)
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL)
    last_restocked = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "inventory item"
        verbose_name_plural = "inventory items"


class PurchaseOrder(models.Model):
    DRAFT = "DRAFT"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (SENT, "Sent"),
        (RECEIVED, "Received"),
        (CANCELLED, "Cancelled"),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"PO #{self.pk} - {self.supplier}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "purchase order"
        verbose_name_plural = "purchase orders"


class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.item} x {self.quantity}"

    class Meta:
        ordering = ["order", "item"]
        verbose_name = "purchase order item"
        verbose_name_plural = "purchase order items"
        constraints = [
            models.UniqueConstraint(fields=["order", "item"], name="unique_item_per_purchase_order"),
        ]
