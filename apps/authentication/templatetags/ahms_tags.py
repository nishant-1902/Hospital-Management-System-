from datetime import date
from decimal import Decimal, InvalidOperation

from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


def _url(name, fallback="#"):
    try:
        return reverse(name)
    except NoReverseMatch:
        return fallback


def _item(label, url_name, icon, active_prefix=None):
    url = _url(url_name)
    return {
        "label": label,
        "url": url,
        "icon": icon,
        "active_prefix": active_prefix or url,
    }


@register.simple_tag
def sidebar_menu(user):
    if not getattr(user, "is_authenticated", False):
        return []

    dashboard_urls = {
        "ADMIN": "authentication:admin_dashboard",
        "DOCTOR": "authentication:doctor_dashboard",
        "PATIENT": "authentication:patient_dashboard",
        "RECEPTIONIST": "authentication:reception_dashboard",
        "PHARMACIST": "authentication:pharmacy_dashboard",
        "LAB_TECH": "authentication:lab_dashboard",
    }

    role = getattr(user, "role", "")
    dashboard = dashboard_urls.get(role, "authentication:home")

    menus = {
        "ADMIN": [
            _item("Dashboard", dashboard, "fa-solid fa-gauge-high", "/dashboard/"),
            _item("Patients", "patients:index", "fa-solid fa-hospital-user", "/patients/"),
            _item("Doctors", "doctors:index", "fa-solid fa-user-doctor", "/doctors/"),
            _item("Appointments", "appointments:index", "fa-solid fa-calendar-check", "/appointments/"),
            _item("EMR", "emr:index", "fa-solid fa-file-medical", "/emr/"),
            _item("Laboratory", "laboratory:index", "fa-solid fa-flask-vial", "/laboratory/"),
            _item("Pharmacy", "pharmacy:index", "fa-solid fa-prescription-bottle-medical", "/pharmacy/"),
            _item("Billing", "billing:index", "fa-solid fa-file-invoice-dollar", "/billing/"),
            _item("Wards & Beds", "wards:index", "fa-solid fa-bed-pulse", "/wards/"),
            _item("Staff", "staff:index", "fa-solid fa-users-gear", "/staff/"),
            _item("Inventory", "inventory:index", "fa-solid fa-boxes-stacked", "/inventory/"),
            _item("Reports", "reports:index", "fa-solid fa-chart-line", "/reports/"),
            _item("Settings", "authentication:profile", "fa-solid fa-gear", "/profile/"),
        ],
        "DOCTOR": [
            _item("Dashboard", dashboard, "fa-solid fa-gauge-high", "/dashboard/"),
            _item("My Appointments", "appointments:index", "fa-solid fa-calendar-check", "/appointments/"),
            _item("Patient Records", "patients:index", "fa-solid fa-notes-medical", "/patients/"),
            _item("Prescriptions", "emr:index", "fa-solid fa-prescription", "/emr/"),
            _item("Lab Orders", "laboratory:index", "fa-solid fa-vials", "/laboratory/"),
            _item("My Schedule", "doctors:index", "fa-solid fa-calendar-days", "/doctors/"),
            _item("Analytics", "reports:index", "fa-solid fa-chart-simple", "/reports/"),
        ],
        "PATIENT": [
            _item("Dashboard", dashboard, "fa-solid fa-gauge-high", "/dashboard/"),
            _item("Book Appointment", "appointments:index", "fa-solid fa-calendar-plus", "/appointments/"),
            _item("My Records", "emr:index", "fa-solid fa-folder-open", "/emr/"),
            _item("My Prescriptions", "pharmacy:index", "fa-solid fa-prescription", "/pharmacy/"),
            _item("Lab Results", "laboratory:index", "fa-solid fa-square-poll-vertical", "/laboratory/"),
            _item("My Bills", "billing:index", "fa-solid fa-receipt", "/billing/"),
        ],
        "RECEPTIONIST": [
            _item("Dashboard", dashboard, "fa-solid fa-gauge-high", "/dashboard/"),
            _item("Register Patient", "patients:index", "fa-solid fa-user-plus", "/patients/"),
            _item("Appointments", "appointments:index", "fa-solid fa-calendar-check", "/appointments/"),
            _item("Billing", "billing:index", "fa-solid fa-file-invoice-dollar", "/billing/"),
            _item("Bed Admission", "wards:index", "fa-solid fa-bed", "/wards/"),
        ],
        "PHARMACIST": [
            _item("Dashboard", dashboard, "fa-solid fa-gauge-high", "/dashboard/"),
            _item("Dispensing Queue", "pharmacy:index", "fa-solid fa-pills", "/pharmacy/"),
            _item("Drug Stock", "inventory:index", "fa-solid fa-boxes-stacked", "/inventory/"),
            _item("Purchase Orders", "billing:index", "fa-solid fa-cart-shopping", "/billing/"),
            _item("Alerts", "reports:index", "fa-solid fa-triangle-exclamation", "/reports/"),
        ],
        "LAB_TECH": [
            _item("Dashboard", dashboard, "fa-solid fa-gauge-high", "/dashboard/"),
            _item("Test Orders", "laboratory:index", "fa-solid fa-list-check", "/laboratory/"),
            _item("Enter Results", "laboratory:index", "fa-solid fa-keyboard", "/laboratory/"),
            _item("Lab Reports", "reports:index", "fa-solid fa-file-medical-alt", "/reports/"),
            _item("Stock", "inventory:index", "fa-solid fa-warehouse", "/inventory/"),
        ],
    }
    return menus.get(role, [])


@register.simple_tag
def badge_color(status):
    value = str(status or "").strip().lower().replace("_", " ")
    colors = {
        "active": "success",
        "approved": "success",
        "available": "success",
        "completed": "success",
        "confirmed": "success",
        "paid": "success",
        "success": "success",
        "pending": "warning",
        "scheduled": "primary",
        "processing": "info",
        "in progress": "info",
        "admitted": "info",
        "inactive": "secondary",
        "draft": "secondary",
        "cancelled": "danger",
        "canceled": "danger",
        "failed": "danger",
        "overdue": "danger",
        "rejected": "danger",
        "unpaid": "danger",
    }
    return colors.get(value, "secondary")


@register.simple_tag
def currency(value):
    try:
        amount = Decimal(value or 0)
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal("0")
    return f"₹{amount:,.2f}"


@register.simple_tag
def age(dob):
    if not dob:
        return ""
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


@register.filter
def startswith(value, prefix):
    return str(value or "").startswith(str(prefix or ""))
