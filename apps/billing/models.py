from django.conf import settings
from django.db import models


class Bill(models.Model):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    REFUNDED = "REFUNDED"

    PAYMENT_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PARTIAL, "Partial"),
        (PAID, "Paid"),
        (REFUNDED, "Refunded"),
    ]

    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    INSURANCE = "INSURANCE"
    WAIVER = "WAIVER"

    PAYMENT_METHOD_CHOICES = [
        (CASH, "Cash"),
        (CARD, "Card"),
        (UPI, "UPI"),
        (INSURANCE, "Insurance"),
        (WAIVER, "Waiver"),
    ]

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT)
    appointment = models.ForeignKey("appointments.Appointment", null=True, blank=True, on_delete=models.SET_NULL)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    insurance_claim = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bill #{self.pk} - {self.patient}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "bill"
        verbose_name_plural = "bills"


class BillItem(models.Model):
    CONSULTATION = "CONSULTATION"
    LAB = "LAB"
    PHARMACY = "PHARMACY"
    WARD = "WARD"
    PROCEDURE = "PROCEDURE"
    OTHER = "OTHER"

    ITEM_TYPE_CHOICES = [
        (CONSULTATION, "Consultation"),
        (LAB, "Lab"),
        (PHARMACY, "Pharmacy"),
        (WARD, "Ward"),
        (PROCEDURE, "Procedure"),
        (OTHER, "Other"),
    ]

    bill = models.ForeignKey(Bill, related_name="items", on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    description = models.CharField(max_length=200)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.bill}"

    class Meta:
        ordering = ["bill", "id"]
        verbose_name = "bill item"
        verbose_name_plural = "bill items"


class Payment(models.Model):
    bill = models.ForeignKey(Bill, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20)
    reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Payment #{self.pk} - {self.amount}"

    class Meta:
        ordering = ["-paid_at"]
        verbose_name = "payment"
        verbose_name_plural = "payments"
