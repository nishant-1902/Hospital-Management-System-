from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class AppointmentsHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "appointments", "status": "ok"})


urlpatterns = [
    path("health/", AppointmentsHealthAPIView.as_view(), name="health"),
]
