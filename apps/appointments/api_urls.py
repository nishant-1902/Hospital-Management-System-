from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_views import AppointmentViewSet, AvailableSlotsAPIView


class AppointmentsHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "appointments", "status": "ok"})


router = DefaultRouter()
router.register("", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("health/", AppointmentsHealthAPIView.as_view(), name="health"),
    path("slots/", AvailableSlotsAPIView.as_view(), name="slots"),
    path("", include(router.urls)),
]
