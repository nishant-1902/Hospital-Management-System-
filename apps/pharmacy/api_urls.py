from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class PharmacyHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "pharmacy", "status": "ok"})


urlpatterns = [
    path("health/", PharmacyHealthAPIView.as_view(), name="health"),
]
