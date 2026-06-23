import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from apps.appointments.models import Appointment
from apps.doctors.models import Doctor
from apps.patients.models import Patient
from apps.pharmacy.models import Medicine

from .forms import MedicalRecordForm, PrescriptionInlineFormSet
from .models import EMRAttachment, MedicalRecord


class EMRPermissionMixin(LoginRequiredMixin):
    allowed_roles = {"ADMIN", "DOCTOR"}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) not in self.allowed_roles:
            messages.error(request, "You do not have permission to access EMR.")
            return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)


def get_doctor_for_user(user):
    return Doctor.objects.filter(user=user).first()


class MedicalRecordCreateView(EMRPermissionMixin, View):
    template_name = "emr/create.html"

    def get_appointment(self):
        return get_object_or_404(
            Appointment.objects.select_related("patient", "doctor", "doctor__department"),
            pk=self.kwargs["appointment_id"],
        )

    def get(self, request, *args, **kwargs):
        appointment = self.get_appointment()
        if not self.can_consult(request.user, appointment):
            messages.error(request, "You cannot create a record for this appointment.")
            return redirect("appointments:detail", pk=appointment.pk)
        existing = MedicalRecord.objects.filter(appointment=appointment).first()
        if existing:
            return redirect("emr:detail", pk=existing.pk)
        record = MedicalRecord(appointment=appointment, patient=appointment.patient, doctor=appointment.doctor)
        form = MedicalRecordForm(instance=record, initial=self.get_draft(request, appointment.pk))
        formset = PrescriptionInlineFormSet(instance=record)
        return self.render_form(request, appointment, form, formset)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        appointment = self.get_appointment()
        if request.headers.get("x-requested-with") == "XMLHttpRequest" and request.POST.get("draft") == "1":
            self.save_draft(request, appointment.pk)
            return JsonResponse({"saved": True})
        if not self.can_consult(request.user, appointment):
            messages.error(request, "You cannot create a record for this appointment.")
            return redirect("appointments:detail", pk=appointment.pk)
        existing = MedicalRecord.objects.filter(appointment=appointment).first()
        if existing:
            messages.info(request, "A medical record already exists for this appointment.")
            return redirect("emr:update", pk=existing.pk)

        record = MedicalRecord(appointment=appointment, patient=appointment.patient, doctor=appointment.doctor)
        form = MedicalRecordForm(request.POST, request.FILES, instance=record)
        formset = PrescriptionInlineFormSet(request.POST, instance=record)
        if form.is_valid() and formset.is_valid():
            record = form.save()
            formset.instance = record
            formset.save()
            for file in form.cleaned_data.get("attachments", []):
                EMRAttachment.objects.create(record=record, file=file, label=file.name)
            request.session.pop(self.draft_key(appointment.pk), None)
            messages.success(request, "Medical record saved.")
            return redirect("emr:detail", pk=record.pk)
        return self.render_form(request, appointment, form, formset)

    def render_form(self, request, appointment, form, formset):
        return render(
            request,
            self.template_name,
            {
                "appointment": appointment,
                "patient": appointment.patient,
                "form": form,
                "formset": formset,
                "medicines": Medicine.objects.filter(is_active=True).order_by("name"),
                "breadcrumbs": [
                    {"label": "Appointments", "url": reverse_lazy("appointments:index")},
                    {"label": f"Appointment #{appointment.pk}", "url": reverse_lazy("appointments:detail", kwargs={"pk": appointment.pk})},
                    {"label": "Consultation"},
                ],
                "is_update": False,
            },
        )

    def can_consult(self, user, appointment):
        return getattr(user, "role", None) == "ADMIN" or appointment.doctor.user_id == user.id

    def draft_key(self, appointment_id):
        return f"emr_draft_{appointment_id}"

    def get_draft(self, request, appointment_id):
        return request.session.get(self.draft_key(appointment_id), {})

    def save_draft(self, request, appointment_id):
        request.session[self.draft_key(appointment_id)] = {
            "diagnosis": request.POST.get("diagnosis", ""),
            "icd10_code": request.POST.get("icd10_code", ""),
            "treatment": request.POST.get("treatment", ""),
            "soap_notes": request.POST.get("soap_notes", ""),
        }
        request.session.modified = True


class MedicalRecordDetailView(EMRPermissionMixin, DetailView):
    model = MedicalRecord
    template_name = "emr/detail.html"
    context_object_name = "record"

    def get_queryset(self):
        return MedicalRecord.objects.select_related("appointment", "patient", "doctor").prefetch_related(
            "attachments", "prescriptions__medicine"
        )


class RecordOwnerOrAdminMixin(EMRPermissionMixin, UserPassesTestMixin):
    def test_func(self):
        record = self.get_object()
        return getattr(self.request.user, "role", None) == "ADMIN" or record.doctor.user_id == self.request.user.id


class MedicalRecordUpdateView(RecordOwnerOrAdminMixin, UpdateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = "emr/create.html"
    context_object_name = "record"

    def get_queryset(self):
        return MedicalRecord.objects.select_related("appointment", "patient", "doctor")

    def get_success_url(self):
        return reverse_lazy("emr:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["appointment"] = self.object.appointment
        context["patient"] = self.object.patient
        context["formset"] = PrescriptionInlineFormSet(self.request.POST or None, instance=self.object)
        context["medicines"] = Medicine.objects.filter(is_active=True).order_by("name")
        context["is_update"] = True
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            for file in form.cleaned_data.get("attachments", []):
                EMRAttachment.objects.create(record=self.object, file=file, label=file.name)
            messages.success(self.request, "Medical record updated.")
            return redirect(self.get_success_url())
        return self.form_invalid(form)


class PatientEMRHistoryView(EMRPermissionMixin, ListView):
    model = MedicalRecord
    template_name = "emr/history.html"
    context_object_name = "records"

    def dispatch(self, request, *args, **kwargs):
        self.patient = get_object_or_404(Patient, pk=kwargs["patient_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            MedicalRecord.objects.filter(patient=self.patient)
            .select_related("doctor", "appointment")
            .prefetch_related("prescriptions__medicine", "attachments")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = self.patient
        return context


class ICD10LookupAPIView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        fixture = Path(__file__).resolve().parent / "fixtures" / "top_500_icd10.json"
        data = json.loads(fixture.read_text(encoding="utf-8"))
        if query:
            data = [
                item
                for item in data
                if query in item["code"].lower() or query in item["description"].lower()
            ]
        return JsonResponse({"results": data[:20]})
