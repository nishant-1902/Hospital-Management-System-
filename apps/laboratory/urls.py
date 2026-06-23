from django.urls import path
from django.views.generic import TemplateView

from .views import (
    LabOrderCreateView,
    LabOrderDetailView,
    LabOrderListView,
    LabReportView,
    LabResultEntryView,
    LabTestCatalogueView,
)

app_name = "laboratory"

urlpatterns = [
    path("", TemplateView.as_view(template_name="laboratory/index.html"), name="index"),
    path("orders/", LabOrderListView.as_view(), name="order_list"),
    path("orders/create/", LabOrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", LabOrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/results/", LabResultEntryView.as_view(), name="result_entry"),
    path("orders/<int:pk>/report/", LabReportView.as_view(), name="report"),
    path("tests/", LabTestCatalogueView.as_view(), name="test_catalogue"),
]
