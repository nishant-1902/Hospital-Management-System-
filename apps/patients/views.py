import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.appointments.models import Appointment
from apps.billing.models import Bill
from apps.emr.models import MedicalRecord
from apps.pharmacy.models import Prescription
from apps.wards.models import Admission, Bed

from .forms import PatientForm
from .models import Patient


class PatientPermissionMixin(LoginRequiredMixin):
    allowed_roles = {"ADMIN", "DOCTOR", "RECEPTIONIST", "PHARMACIST", "LAB_TECH"}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) not in self.allowed_roles:
            messages.error(request, "You do not have permission to access patient management.")
            return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)


class PatientWritePermissionMixin(PatientPermissionMixin, UserPassesTestMixin):
    write_roles = {"ADMIN", "RECEPTIONIST"}

    def test_func(self):
        return getattr(self.request.user, "role", None) in self.write_roles


class PatientListView(PatientPermissionMixin, ListView):
    model = Patient
    template_name = "patients/list.html"
    context_object_name = "patients"
    paginate_by = 20

    def get_queryset(self):
        queryset = Patient.objects.filter(is_active=True).order_by("name")
        query = self.request.GET.get("q", "").strip()
        gender = self.request.GET.get("gender", "").strip()
        blood_group = self.request.GET.get("blood_group", "").strip()

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(phone__icontains=query) | Q(pid__icontains=query)
            )
        if gender:
            queryset = queryset.filter(gender=gender)
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        if request.GET.get("export") == "csv":
            return self.export_csv(self.object_list)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gender_choices"] = Patient.GENDER_CHOICES
        context["blood_group_choices"] = Patient.BLOOD_GROUP_CHOICES
        context["breadcrumbs"] = [{"label": "Patients"}]
        return context

    def export_csv(self, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="patients.csv"'
        writer = csv.writer(response)
        writer.writerow(["PID", "Name", "Phone", "Gender", "DOB", "Blood Group", "Address"])
        for patient in queryset:
            writer.writerow([
                patient.pid,
                patient.name,
                patient.phone,
                patient.get_gender_display(),
                patient.dob,
                patient.blood_group,
                patient.address,
            ])
        return response


class PatientCreateView(PatientWritePermissionMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = "patients/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Patient registered successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("patients:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Register Patient"
        context["submit_label"] = "Register Patient"
        context["breadcrumbs"] = [
            {"label": "Patients", "url": reverse_lazy("patients:index")},
            {"label": "Register Patient"},
        ]
        return context


class PatientDetailView(PatientPermissionMixin, DetailView):
    model = Patient
    template_name = "patients/detail.html"
    context_object_name = "patient"

    def get_queryset(self):
        return Patient.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object
        appointments = (
            Appointment.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("-date", "-time")[:20]
        )
        medical_records = (
            MedicalRecord.objects.filter(patient=patient)
            .select_related("doctor", "appointment")
            .prefetch_related("prescriptions__medicine")
            .order_by("-created_at")[:10]
        )
        context["appointments"] = appointments
        context["medical_records"] = medical_records
        context["active_prescriptions"] = (
            Prescription.objects.filter(record__patient=patient, is_dispensed=False)
            .select_related("medicine", "record")
            .order_by("-record__created_at")[:10]
        )
        context["recent_bills"] = Bill.objects.filter(patient=patient).order_by("-created_at")[:10]
        context["current_bed"] = (
            Bed.objects.filter(patient=patient, status=Bed.OCCUPIED)
            .select_related("ward")
            .first()
        )
        context["active_admission"] = (
            Admission.objects.filter(patient=patient, is_active=True)
            .select_related("bed__ward")
            .first()
        )
        context["breadcrumbs"] = [
            {"label": "Patients", "url": reverse_lazy("patients:index")},
            {"label": patient.name},
        ]
        return context


class PatientUpdateView(PatientWritePermissionMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = "patients/form.html"

    def get_queryset(self):
        return Patient.objects.filter(is_active=True)

    def form_valid(self, form):
        messages.success(self.request, "Patient updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("patients:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Patient"
        context["submit_label"] = "Save Changes"
        context["breadcrumbs"] = [
            {"label": "Patients", "url": reverse_lazy("patients:index")},
            {"label": self.object.name, "url": reverse_lazy("patients:detail", kwargs={"pk": self.object.pk})},
            {"label": "Edit"},
        ]
        return context


class PatientDeleteView(PatientWritePermissionMixin, DeleteView):
    model = Patient
    template_name = "patients/confirm_delete.html"
    context_object_name = "patient"
    success_url = reverse_lazy("patients:index")

    def get_queryset(self):
        return Patient.objects.filter(is_active=True)

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active", "updated_at"])
        messages.success(self.request, "Patient archived successfully.")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = [
            {"label": "Patients", "url": reverse_lazy("patients:index")},
            {"label": self.object.name, "url": reverse_lazy("patients:detail", kwargs={"pk": self.object.pk})},
            {"label": "Delete"},
        ]
        return context


class PatientSearchAPIView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        patients = Patient.objects.filter(is_active=True)
        if query:
            patients = patients.filter(
                Q(name__icontains=query) | Q(phone__icontains=query) | Q(pid__icontains=query)
            )
        results = [
            {
                "id": patient.pk,
                "pid": patient.pid,
                "name": patient.name,
                "phone": patient.phone,
                "gender": patient.get_gender_display(),
                "dob": patient.dob.isoformat() if patient.dob else None,
            }
            for patient in patients.order_by("name")[:10]
        ]
        return JsonResponse({"results": results})
