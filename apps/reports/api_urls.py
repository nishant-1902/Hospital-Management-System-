from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class ReportsHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "reports", "status": "ok"})


urlpatterns = [
    path("health/", ReportsHealthAPIView.as_view(), name="health"),
]
