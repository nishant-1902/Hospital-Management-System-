import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django import forms

from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "user",
            "name",
            "gender",
            "dob",
            "phone",
            "address",
            "blood_group",
            "photo",
            "id_document",
            "is_active",
        ]
        widgets = {
            "gender": forms.RadioSelect,
            "dob": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["blood_group"].empty_label = "Select blood group"
        self.fields["user"].required = False
        self.fields["photo"].required = False
        self.fields["id_document"].required = False
        self.fields["is_active"].required = False

        for field in self.fields.values():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.setdefault("class", "form-control")

        self.fields["blood_group"].widget.attrs["class"] = "form-select"
        self.fields["user"].widget.attrs["class"] = "form-select"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.form_tag = False
        self.helper.label_class = "form-label"
        self.helper.field_class = ""
        self.helper.layout = Layout(
            Div(
                Div(Field("user"), css_class="col-md-6"),
                Div(Field("name"), css_class="col-md-6"),
                Div(Field("gender"), css_class="col-md-6"),
                Div(Field("dob"), css_class="col-md-6"),
                Div(Field("phone"), css_class="col-md-6"),
                Div(Field("blood_group"), css_class="col-md-6"),
                Div(Field("address"), css_class="col-12"),
                Div(Field("photo"), css_class="col-md-6"),
                Div(Field("id_document"), css_class="col-md-6"),
                Div(Field("is_active"), css_class="col-12"),
                css_class="row g-3",
            )
        )

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = re.sub(r"\D", "", phone)
        if len(digits) != 10:
            raise forms.ValidationError("Enter a valid 10-digit phone number.")
        return digits
