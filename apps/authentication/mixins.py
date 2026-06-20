from functools import wraps

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.allowed_roles:
            if request.user.role not in self.allowed_roles:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access that page.")
        login_url = reverse("authentication:login")
        return redirect(f"{login_url}?next={self.request.get_full_path()}")


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["ADMIN"]


class DoctorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["DOCTOR"]


class PatientRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["PATIENT"]


class ReceptionistRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["RECEPTIONIST"]


class PharmacistRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["PHARMACIST"]


class LabTechRequiredMixin(RoleRequiredMixin):
    allowed_roles = ["LAB_TECH"]


class MultiRoleRequiredMixin(RoleRequiredMixin):
    allowed_roles = []


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please log in to continue.")
                login_url = reverse("authentication:login")
                return redirect(f"{login_url}?next={request.get_full_path()}")
            if request.user.role not in allowed_roles:
                messages.error(request, "You do not have permission to access that page.")
                login_url = reverse("authentication:login")
                return redirect(f"{login_url}?next={request.get_full_path()}")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
