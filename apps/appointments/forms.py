from django import forms

from apps.doctors.models import Doctor
from apps.patients.models import Patient

from .models import Appointment
from .services import get_available_slots


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "time", "status", "type", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.filter(is_active=True).order_by("name")
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True).order_by("name")
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class AppointmentBookingForm(forms.Form):
    patient = forms.ModelChoiceField(queryset=Patient.objects.none())
    specialization = forms.CharField(required=False)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.none())
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    type = forms.ChoiceField(choices=Appointment.TYPE_CHOICES)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.filter(is_active=True).order_by("name")
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True).order_by("name")
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get("doctor")
        date = cleaned.get("date")
        time = cleaned.get("time")
        if doctor and date and time and time not in get_available_slots(doctor, date):
            raise forms.ValidationError("The selected slot is no longer available.")
        return cleaned


class AppointmentCancelForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Cancellation reason"}),
        required=False,
    )
