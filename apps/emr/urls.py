from django.urls import path

from .views import (
    ICD10LookupAPIView,
    MedicalRecordCreateView,
    MedicalRecordDetailView,
    MedicalRecordUpdateView,
    PatientEMRHistoryView,
)

app_name = "emr"

urlpatterns = [
    path("appointment/<int:appointment_id>/create/", MedicalRecordCreateView.as_view(), name="create"),
    path("records/<int:pk>/", MedicalRecordDetailView.as_view(), name="detail"),
    path("records/<int:pk>/edit/", MedicalRecordUpdateView.as_view(), name="update"),
    path("patients/<int:patient_id>/history/", PatientEMRHistoryView.as_view(), name="history"),
    path("icd10/", ICD10LookupAPIView.as_view(), name="icd10"),
]
