from django.urls import path
from django.views.generic import TemplateView

app_name = "wards"

urlpatterns = [
    path("", TemplateView.as_view(template_name="wards/index.html"), name="index"),
]
