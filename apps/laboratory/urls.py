from django.urls import path
from django.views.generic import TemplateView

app_name = "laboratory"

urlpatterns = [
    path("", TemplateView.as_view(template_name="laboratory/index.html"), name="index"),
]
