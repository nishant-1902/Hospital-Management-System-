from django.urls import path

app_name = "patients"

from .views import (
    PatientCreateView,
    PatientDeleteView,
    PatientDetailView,
    PatientListView,
    PatientSearchAPIView,
    PatientUpdateView,
)

urlpatterns = [
    path("", PatientListView.as_view(), name="index"),
    path("list/", PatientListView.as_view(), name="list"),
    path("register/", PatientCreateView.as_view(), name="create"),
    path("search/", PatientSearchAPIView.as_view(), name="search"),
    path("<int:pk>/", PatientDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", PatientUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", PatientDeleteView.as_view(), name="delete"),
]
