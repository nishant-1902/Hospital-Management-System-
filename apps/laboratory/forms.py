from django import forms
from django.forms import modelformset_factory

from apps.doctors.models import Doctor

from .models import LabOrder, LabOrderItem, LabTest


class LabOrderForm(forms.ModelForm):
    tests = forms.ModelMultipleChoiceField(
        queryset=LabTest.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = LabOrder
        fields = ["patient", "doctor", "tests", "priority", "status"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-select"}),
            "doctor": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tests"].queryset = LabTest.objects.order_by("category", "name")
        self.fields["doctor"].queryset = Doctor.objects.filter(is_active=True).order_by("name")
        self.fields["status"].initial = LabOrder.ORDERED
        if getattr(user, "role", None) == "DOCTOR":
            doctor = Doctor.objects.filter(user=user).first()
            if doctor:
                self.fields["doctor"].initial = doctor
                self.fields["doctor"].disabled = True

    def clean_doctor(self):
        if self.fields["doctor"].disabled:
            return self.fields["doctor"].initial
        return self.cleaned_data["doctor"]


class LabOrderFilterForm(forms.Form):
    status = forms.ChoiceField(required=False, choices=[("", "All statuses")] + LabOrder.STATUS_CHOICES)
    priority = forms.ChoiceField(required=False, choices=[("", "All priorities")] + LabOrder.PRIORITY_CHOICES)
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


class LabOrderItemResultForm(forms.ModelForm):
    class Meta:
        model = LabOrderItem
        fields = ["result", "verified"]
        widgets = {
            "result": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "verified": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


LabResultFormSet = modelformset_factory(
    LabOrderItem,
    form=LabOrderItemResultForm,
    extra=0,
    can_delete=False,
)


class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ["name", "code", "category", "normal_range", "unit", "price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "normal_range": forms.TextInput(attrs={"class": "form-control", "placeholder": "70-100, <200, >0.5"}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }
