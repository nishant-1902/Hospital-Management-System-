from django.urls import path
from django.views.generic import TemplateView

app_name = "doctors"

urlpatterns = [
    path("", TemplateView.as_view(template_name="doctors/index.html"), name="index"),
]
