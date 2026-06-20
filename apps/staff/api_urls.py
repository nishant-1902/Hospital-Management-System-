from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class StaffHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "staff", "status": "ok"})


urlpatterns = [
    path("health/", StaffHealthAPIView.as_view(), name="health"),
]
