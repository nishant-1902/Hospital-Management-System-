from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_views import PatientViewSet
from .views import PatientSearchAPIView


class PatientsHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "patients", "status": "ok"})


router = DefaultRouter()
router.register("", PatientViewSet, basename="patient")

urlpatterns = [
    path("health/", PatientsHealthAPIView.as_view(), name="health"),
    path("search/", PatientSearchAPIView.as_view(), name="search"),
    path("", include(router.urls)),
]
