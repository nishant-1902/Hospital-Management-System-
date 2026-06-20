from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class WardsHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "wards", "status": "ok"})


urlpatterns = [
    path("health/", WardsHealthAPIView.as_view(), name="health"),
]
