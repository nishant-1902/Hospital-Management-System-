from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from apps.doctors.models import Doctor

from .forms import AppointmentBookingForm, AppointmentCancelForm, AppointmentForm
from .models import Appointment
from .services import book_appointment, cancel_appointment


class AppointmentPermissionMixin(LoginRequiredMixin):
    allowed_roles = {"ADMIN", "DOCTOR", "RECEPTIONIST", "PATIENT"}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) not in self.allowed_roles:
            messages.error(request, "You do not have permission to access appointments.")
            return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)


class AppointmentListView(AppointmentPermissionMixin, ListView):
    model = Appointment
    template_name = "appointments/list.html"
    context_object_name = "appointments"
    paginate_by = 20

    def get_queryset(self):
        queryset = Appointment.objects.select_related("patient", "doctor").all()
        date = self.request.GET.get("date", "").strip()
        start_date = self.request.GET.get("start_date", "").strip()
        end_date = self.request.GET.get("end_date", "").strip()
        doctor = self.request.GET.get("doctor", "").strip()
        status = self.request.GET.get("status", "").strip()
        appointment_type = self.request.GET.get("type", "").strip()
        query = self.request.GET.get("q", "").strip()

        if date:
            queryset = queryset.filter(date=date)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if doctor:
            queryset = queryset.filter(doctor_id=doctor)
        if status:
            queryset = queryset.filter(status=status)
        if appointment_type:
            queryset = queryset.filter(type=appointment_type)
        if query:
            queryset = queryset.filter(Q(patient__name__icontains=query) | Q(patient__pid__icontains=query))
        return queryset.order_by("-date", "-time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors"] = Doctor.objects.filter(is_active=True).order_by("name")
        context["status_choices"] = Appointment.STATUS_CHOICES
        context["type_choices"] = Appointment.TYPE_CHOICES
        context["breadcrumbs"] = [{"label": "Appointments"}]
        return context


class AppointmentCreateView(AppointmentPermissionMixin, FormView):
    template_name = "appointments/create.html"
    form_class = AppointmentBookingForm

    def form_valid(self, form):
        appointment = book_appointment(
            patient=form.cleaned_data["patient"],
            doctor=form.cleaned_data["doctor"],
            date=form.cleaned_data["date"],
            time=form.cleaned_data["time"],
            type=form.cleaned_data["type"],
            notes=form.cleaned_data.get("notes", ""),
        )
        messages.success(self.request, "Appointment booked successfully.")
        return redirect("appointments:detail", pk=appointment.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["specializations"] = (
            Doctor.objects.filter(is_active=True).values_list("specialization", flat=True).distinct().order_by("specialization")
        )
        context["doctors"] = Doctor.objects.filter(is_active=True).select_related("department").order_by("name")
        context["breadcrumbs"] = [{"label": "Appointments", "url": reverse_lazy("appointments:index")}, {"label": "Book"}]
        return context


class AppointmentDetailView(AppointmentPermissionMixin, DetailView):
    model = Appointment
    template_name = "appointments/detail.html"
    context_object_name = "appointment"

    def get_queryset(self):
        return Appointment.objects.select_related("patient", "doctor", "doctor__department")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_form"] = AppointmentCancelForm()
        context["breadcrumbs"] = [
            {"label": "Appointments", "url": reverse_lazy("appointments:index")},
            {"label": f"Appointment #{self.object.pk}"},
        ]
        return context

    def post(self, request, *args, **kwargs):
        appointment = self.get_object()
        status = request.POST.get("status")
        allowed = {value for value, _ in Appointment.STATUS_CHOICES}
        if status in allowed:
            appointment.status = status
            appointment.save(update_fields=["status"])
            messages.success(request, "Appointment status updated.")
        else:
            messages.error(request, "Invalid appointment status.")
        return redirect("appointments:detail", pk=appointment.pk)


class AppointmentUpdateView(AppointmentPermissionMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/form.html"

    def get_success_url(self):
        return reverse_lazy("appointments:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Appointment updated successfully.")
        return super().form_valid(form)


class AppointmentCancelView(AppointmentPermissionMixin, FormView):
    form_class = AppointmentCancelForm
    template_name = "appointments/cancel.html"

    def dispatch(self, request, *args, **kwargs):
        self.appointment = get_object_or_404(Appointment.objects.select_related("patient", "doctor"), pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        cancel_appointment(self.appointment, form.cleaned_data.get("reason", ""))
        messages.success(self.request, "Appointment cancelled.")
        return redirect("appointments:detail", pk=self.appointment.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appointment"] = self.appointment
        return context


class TodaysAppointmentsView(AppointmentPermissionMixin, ListView):
    model = Appointment
    template_name = "appointments/todays.html"
    context_object_name = "appointments"

    def get_queryset(self):
        return (
            Appointment.objects.select_related("patient", "doctor")
            .filter(date=timezone.localdate())
            .order_by("time", "token_no")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        context["breadcrumbs"] = [{"label": "Appointments", "url": reverse_lazy("appointments:index")}, {"label": "Today"}]
        return context
