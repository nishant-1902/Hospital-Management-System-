from django.urls import path

from .views import (
    DepartmentCreateView,
    DepartmentListView,
    DepartmentUpdateView,
    DoctorCreateView,
    DoctorDetailView,
    DoctorListView,
    DoctorScheduleView,
    DoctorUpdateView,
)

app_name = "doctors"

urlpatterns = [
    path("", DoctorListView.as_view(), name="index"),
    path("create/", DoctorCreateView.as_view(), name="create"),
    path("departments/", DepartmentListView.as_view(), name="departments"),
    path("departments/create/", DepartmentCreateView.as_view(), name="department_create"),
    path("departments/<int:pk>/edit/", DepartmentUpdateView.as_view(), name="department_update"),
    path("<int:pk>/", DoctorDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", DoctorUpdateView.as_view(), name="update"),
    path("<int:pk>/schedule/", DoctorScheduleView.as_view(), name="schedule"),
]
