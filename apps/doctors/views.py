from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.appointments.models import Appointment
from apps.appointments.services import parse_available_days

from .forms import DepartmentForm, DoctorForm, WEEKDAY_CHOICES
from .models import Department, Doctor


class DoctorPermissionMixin(LoginRequiredMixin):
    allowed_roles = {"ADMIN", "DOCTOR", "RECEPTIONIST"}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) not in self.allowed_roles:
            messages.error(request, "You do not have permission to access doctor management.")
            return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(DoctorPermissionMixin, UserPassesTestMixin):
    def test_func(self):
        return getattr(self.request.user, "role", None) == "ADMIN"


class DoctorListView(DoctorPermissionMixin, ListView):
    model = Doctor
    template_name = "doctors/list.html"
    context_object_name = "doctors"

    def get_queryset(self):
        queryset = Doctor.objects.select_related("department", "user").filter(is_active=True)
        query = self.request.GET.get("q", "").strip()
        specialization = self.request.GET.get("specialization", "").strip()
        department = self.request.GET.get("department", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(specialization__icontains=query)
                | Q(user__email__icontains=query)
                | Q(department__name__icontains=query)
            )
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        if department:
            queryset = queryset.filter(department_id=department)
        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["specializations"] = (
            Doctor.objects.filter(is_active=True).values_list("specialization", flat=True).distinct().order_by("specialization")
        )
        context["departments"] = Department.objects.all()
        context["breadcrumbs"] = [{"label": "Doctors"}]
        return context


class DoctorCreateView(AdminRequiredMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "doctors/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Doctor created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("doctors:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Doctor"
        context["submit_label"] = "Create Doctor"
        context["breadcrumbs"] = [{"label": "Doctors", "url": reverse_lazy("doctors:index")}, {"label": "Add"}]
        return context


class DoctorDetailView(DoctorPermissionMixin, DetailView):
    model = Doctor
    template_name = "doctors/detail.html"
    context_object_name = "doctor"

    def get_queryset(self):
        return Doctor.objects.select_related("department", "user").filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object
        context["availability_grid"] = build_availability_grid(doctor)
        context["appointments"] = Appointment.objects.filter(doctor=doctor).select_related("patient").order_by("-date", "-time")[:20]
        context["breadcrumbs"] = [{"label": "Doctors", "url": reverse_lazy("doctors:index")}, {"label": doctor.name}]
        return context


class DoctorUpdateView(AdminRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = "doctors/form.html"

    def get_queryset(self):
        return Doctor.objects.select_related("user").filter(is_active=True)

    def form_valid(self, form):
        messages.success(self.request, "Doctor updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("doctors:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Doctor"
        context["submit_label"] = "Save Changes"
        context["breadcrumbs"] = [
            {"label": "Doctors", "url": reverse_lazy("doctors:index")},
            {"label": self.object.name, "url": reverse_lazy("doctors:detail", kwargs={"pk": self.object.pk})},
            {"label": "Edit"},
        ]
        return context


class DoctorScheduleView(DoctorPermissionMixin, DetailView):
    model = Doctor
    template_name = "doctors/schedule.html"
    context_object_name = "doctor"

    def get_queryset(self):
        return Doctor.objects.select_related("department").filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object
        appointments = Appointment.objects.filter(doctor=doctor).select_related("patient")
        events = []
        colors = {
            Appointment.SCHEDULED: "#2E86C1",
            Appointment.CONFIRMED: "#27AE60",
            Appointment.IN_PROGRESS: "#F39C12",
            Appointment.COMPLETED: "#1A5276",
            Appointment.CANCELLED: "#E74C3C",
        }
        for appointment in appointments:
            starts_at = datetime.combine(appointment.date, appointment.time)
            events.append(
                {
                    "title": f"{appointment.token_no or '-'} - {appointment.patient.name}",
                    "start": starts_at.isoformat(),
                    "end": (starts_at + timedelta(minutes=15)).isoformat(),
                    "backgroundColor": colors.get(appointment.status, "#6c757d"),
                    "borderColor": colors.get(appointment.status, "#6c757d"),
                    "url": reverse("appointments:detail", kwargs={"pk": appointment.pk}),
                }
            )
        context["events"] = events
        context["breadcrumbs"] = [
            {"label": "Doctors", "url": reverse_lazy("doctors:index")},
            {"label": doctor.name, "url": reverse_lazy("doctors:detail", kwargs={"pk": doctor.pk})},
            {"label": "Schedule"},
        ]
        return context


class DepartmentListView(AdminRequiredMixin, ListView):
    model = Department
    template_name = "doctors/departments.html"
    context_object_name = "departments"


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "doctors/department_form.html"
    success_url = reverse_lazy("doctors:departments")

    def form_valid(self, form):
        messages.success(self.request, "Department created successfully.")
        return super().form_valid(form)


class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "doctors/department_form.html"
    success_url = reverse_lazy("doctors:departments")

    def form_valid(self, form):
        messages.success(self.request, "Department updated successfully.")
        return super().form_valid(form)


def build_availability_grid(doctor):
    day_lookup = dict(WEEKDAY_CHOICES)
    available_days = parse_available_days(doctor.available_days)
    slots = []
    if doctor.consult_start and doctor.consult_end:
        current = datetime.combine(date.today(), doctor.consult_start)
        end = datetime.combine(date.today(), doctor.consult_end)
        while current < end:
            slots.append(current.time())
            current += timedelta(minutes=15)

    return [
        {
            "value": value,
            "label": label,
            "available": int(value) in available_days,
            "slots": slots if int(value) in available_days else [],
        }
        for value, label in day_lookup.items()
    ]
