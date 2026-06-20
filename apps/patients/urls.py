from django.urls import path
from django.views.generic import TemplateView

app_name = "patients"

urlpatterns = [
    path("", TemplateView.as_view(template_name="patients/index.html"), name="index"),
]
