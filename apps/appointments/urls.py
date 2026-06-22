from django.urls import path

from .views import (
    AppointmentCancelView,
    AppointmentCreateView,
    AppointmentDetailView,
    AppointmentListView,
    AppointmentUpdateView,
    TodaysAppointmentsView,
)

app_name = "appointments"

urlpatterns = [
    path("", AppointmentListView.as_view(), name="index"),
    path("book/", AppointmentCreateView.as_view(), name="create"),
    path("today/", TodaysAppointmentsView.as_view(), name="today"),
    path("<int:pk>/", AppointmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", AppointmentUpdateView.as_view(), name="update"),
    path("<int:pk>/cancel/", AppointmentCancelView.as_view(), name="cancel"),
]
