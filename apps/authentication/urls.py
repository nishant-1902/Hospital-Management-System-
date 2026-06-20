from django.urls import path

from .views import DashboardView, LoginView, LogoutView, PasswordResetConfirmView, PasswordResetRequestView, ProfileView

app_name = "authentication"

urlpatterns = [
    path("", LoginView.as_view(), name="home"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password-reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("dashboard/admin/", DashboardView.as_view(role="ADMIN"), name="admin_dashboard"),
    path("dashboard/doctor/", DashboardView.as_view(role="DOCTOR"), name="doctor_dashboard"),
    path("dashboard/patient/", DashboardView.as_view(role="PATIENT"), name="patient_dashboard"),
    path("dashboard/reception/", DashboardView.as_view(role="RECEPTIONIST"), name="reception_dashboard"),
    path("dashboard/pharmacy/", DashboardView.as_view(role="PHARMACIST"), name="pharmacy_dashboard"),
    path("dashboard/lab/", DashboardView.as_view(role="LAB_TECH"), name="lab_dashboard"),
]
