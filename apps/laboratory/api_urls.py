from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class LaboratoryHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "laboratory", "status": "ok"})


urlpatterns = [
    path("health/", LaboratoryHealthAPIView.as_view(), name="health"),
]
