from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.appointments.services import parse_available_days

from .models import Department, Doctor


WEEKDAY_CHOICES = [
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday"),
]


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "location"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
        }


class DoctorForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    available_days = forms.MultipleChoiceField(
        choices=WEEKDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Doctor
        fields = [
            "name",
            "specialization",
            "department",
            "qualification",
            "experience_yrs",
            "available_days",
            "consult_start",
            "consult_end",
            "is_active",
        ]
        widgets = {
            "consult_start": forms.TimeInput(attrs={"type": "time"}),
            "consult_end": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_create = self.instance.pk is None
        user = getattr(self.instance, "user", None)

        if user:
            self.fields["email"].initial = user.email
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["phone"].initial = user.phone

        if self.instance.available_days:
            self.fields["available_days"].initial = [str(day) for day in sorted(parse_available_days(self.instance.available_days))]

        self.fields["password"].required = self.is_create
        self.fields["password"].help_text = "Required for new doctors. Leave blank to keep the current password."

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            elif not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault("class", "form-control")

        self.fields["is_active"].widget.attrs["class"] = "form-check-input"

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(Field("email"), css_class="col-md-6"),
                Div(Field("password"), css_class="col-md-6"),
                Div(Field("first_name"), css_class="col-md-4"),
                Div(Field("last_name"), css_class="col-md-4"),
                Div(Field("phone"), css_class="col-md-4"),
                Div(Field("name"), css_class="col-md-6"),
                Div(Field("specialization"), css_class="col-md-6"),
                Div(Field("department"), css_class="col-md-6"),
                Div(Field("qualification"), css_class="col-md-6"),
                Div(Field("experience_yrs"), css_class="col-md-4"),
                Div(Field("consult_start"), css_class="col-md-4"),
                Div(Field("consult_end"), css_class="col-md-4"),
                Div(Field("available_days"), css_class="col-12"),
                Div(Field("is_active"), css_class="col-12"),
                css_class="row g-3",
            )
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        User = get_user_model()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance.pk and self.instance.user_id:
            queryset = queryset.exclude(pk=self.instance.user_id)
        if queryset.exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("consult_start")
        end = cleaned.get("consult_end")
        if start and end and start >= end:
            raise forms.ValidationError("Consultation end time must be after start time.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        doctor = super().save(commit=False)
        User = get_user_model()
        email = self.cleaned_data["email"]

        if doctor.pk and doctor.user_id:
            user = doctor.user
            user.email = email
            user.username = email
        else:
            user = User(email=email, username=email, role="DOCTOR")

        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.phone = self.cleaned_data.get("phone", "")
        user.role = "DOCTOR"
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        doctor.user = user
        doctor.available_days = ",".join(self.cleaned_data.get("available_days") or [])
        if commit:
            doctor.save()
            self.save_m2m()
        return doctor
