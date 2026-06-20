from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class InventoryHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "inventory", "status": "ok"})


urlpatterns = [
    path("health/", InventoryHealthAPIView.as_view(), name="health"),
]
