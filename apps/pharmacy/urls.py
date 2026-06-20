from django.urls import path
from django.views.generic import TemplateView

app_name = "pharmacy"

urlpatterns = [
    path("", TemplateView.as_view(template_name="pharmacy/index.html"), name="index"),
]
