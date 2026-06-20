from django.urls import path
from django.views.generic import TemplateView

app_name = "appointments"

urlpatterns = [
    path("", TemplateView.as_view(template_name="appointments/index.html"), name="index"),
]
