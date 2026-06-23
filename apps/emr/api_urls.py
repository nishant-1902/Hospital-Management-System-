from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from .views import ICD10LookupAPIView


class EmrHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "emr", "status": "ok"})


urlpatterns = [
    path("health/", EmrHealthAPIView.as_view(), name="health"),
    path("icd10/", ICD10LookupAPIView.as_view(), name="icd10"),
]
