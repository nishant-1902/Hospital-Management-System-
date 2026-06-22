from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_views import DoctorAvailabilityAPIView, DoctorViewSet


class DoctorsHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "doctors", "status": "ok"})


router = DefaultRouter()
router.register("", DoctorViewSet, basename="doctor")

urlpatterns = [
    path("health/", DoctorsHealthAPIView.as_view(), name="health"),
    path("<int:pk>/availability/", DoctorAvailabilityAPIView.as_view(), name="availability"),
    path("", include(router.urls)),
]
