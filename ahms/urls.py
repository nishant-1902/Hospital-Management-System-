from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.authentication.urls")),
    path("patients/", include("apps.patients.urls")),
    path("doctors/", include("apps.doctors.urls")),
    path("appointments/", include("apps.appointments.urls")),
    path("emr/", include("apps.emr.urls")),
    path("laboratory/", include("apps.laboratory.urls")),
    path("pharmacy/", include("apps.pharmacy.urls")),
    path("billing/", include("apps.billing.urls")),
    path("wards/", include("apps.wards.urls")),
    path("staff/", include("apps.staff.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("reports/", include("apps.reports.urls")),
    path("api/v1/auth/", include(("apps.authentication.api_urls", "authentication"), namespace="authentication-api")),
    path("api/v1/patients/", include(("apps.patients.api_urls", "patients"), namespace="patients-api")),
    path("api/v1/doctors/", include(("apps.doctors.api_urls", "doctors"), namespace="doctors-api")),
    path("api/v1/appointments/", include(("apps.appointments.api_urls", "appointments"), namespace="appointments-api")),
    path("api/v1/emr/", include(("apps.emr.api_urls", "emr"), namespace="emr-api")),
    path("api/v1/laboratory/", include(("apps.laboratory.api_urls", "laboratory"), namespace="laboratory-api")),
    path("api/v1/pharmacy/", include(("apps.pharmacy.api_urls", "pharmacy"), namespace="pharmacy-api")),
    path("api/v1/billing/", include(("apps.billing.api_urls", "billing"), namespace="billing-api")),
    path("api/v1/wards/", include(("apps.wards.api_urls", "wards"), namespace="wards-api")),
    path("api/v1/staff/", include(("apps.staff.api_urls", "staff"), namespace="staff-api")),
    path("api/v1/inventory/", include(("apps.inventory.api_urls", "inventory"), namespace="inventory-api")),
    path("api/v1/reports/", include(("apps.reports.api_urls", "reports"), namespace="reports-api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
