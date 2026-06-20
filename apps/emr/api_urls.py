from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class EmrHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "emr", "status": "ok"})


urlpatterns = [
    path("health/", EmrHealthAPIView.as_view(), name="health"),
]
