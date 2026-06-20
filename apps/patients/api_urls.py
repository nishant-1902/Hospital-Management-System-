from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class PatientsHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "patients", "status": "ok"})


urlpatterns = [
    path("health/", PatientsHealthAPIView.as_view(), name="health"),
]
