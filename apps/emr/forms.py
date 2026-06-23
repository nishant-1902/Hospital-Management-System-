from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.pharmacy.models import Medicine, Prescription

from .models import EMRAttachment, MedicalRecord


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]
        return [single_file_clean(data, initial)] if data else []


class MedicalRecordForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={"class": "form-control", "multiple": True}),
    )

    class Meta:
        model = MedicalRecord
        fields = ["diagnosis", "icd10_code", "treatment", "soap_notes"]
        widgets = {
            "diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "icd10_code": forms.TextInput(attrs={"class": "form-control", "list": "icd10Options"}),
            "treatment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "soap_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 12,
                    "placeholder": "S: Subjective\n\nO: Objective\n\nA: Assessment\n\nP: Plan",
                }
            ),
        }


class PrescriptionInlineForm(forms.ModelForm):
    medicine = forms.ModelChoiceField(
        queryset=Medicine.objects.filter(is_active=True).order_by("name"),
        widget=forms.Select(attrs={"class": "form-select medicine-select", "data-medicine-autocomplete": "1"}),
    )

    class Meta:
        model = Prescription
        fields = ["medicine", "dosage", "frequency", "duration_days", "instructions"]
        widgets = {
            "dosage": forms.TextInput(attrs={"class": "form-control", "placeholder": "500 mg"}),
            "frequency": forms.TextInput(attrs={"class": "form-control", "placeholder": "1-0-1"}),
            "duration_days": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "instructions": forms.TextInput(attrs={"class": "form-control", "placeholder": "After food"}),
        }


class EMRAttachmentForm(forms.ModelForm):
    class Meta:
        model = EMRAttachment
        fields = ["file", "label"]


class BasePrescriptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or form.cleaned_data.get("DELETE"):
                continue
            medicine = form.cleaned_data.get("medicine")
            dosage = form.cleaned_data.get("dosage")
            if medicine and not dosage:
                form.add_error("dosage", "Dosage is required when a medicine is selected.")


PrescriptionInlineFormSet = inlineformset_factory(
    MedicalRecord,
    Prescription,
    form=PrescriptionInlineForm,
    formset=BasePrescriptionInlineFormSet,
    extra=1,
    can_delete=True,
)
