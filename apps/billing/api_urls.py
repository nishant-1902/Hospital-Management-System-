from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class BillingHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "billing", "status": "ok"})


urlpatterns = [
    path("health/", BillingHealthAPIView.as_view(), name="health"),
]
