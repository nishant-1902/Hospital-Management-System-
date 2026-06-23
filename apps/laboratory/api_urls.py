from django.urls import include, path
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LabOrder, LabTest
from .serializers import LabOrderSerializer, LabTestSerializer


class LabOrderViewSet(viewsets.ModelViewSet):
    queryset = LabOrder.objects.select_related("patient", "doctor").prefetch_related("laborderitem_set__test")
    serializer_class = LabOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["patient", "doctor", "status", "priority", "ordered_at"]
    search_fields = ["patient__name", "patient__pid", "doctor__name", "tests__name", "tests__code"]
    ordering_fields = ["ordered_at", "priority", "status"]
    ordering = ["-ordered_at"]


class LabTestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get("q", "").strip()
        tests = LabTest.objects.all()
        if query:
            tests = tests.filter(name__icontains=query) | tests.filter(code__icontains=query)
        serializer = LabTestSerializer(tests.distinct().order_by("name")[:25], many=True)
        return Response({"results": serializer.data})


class LaboratoryHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "laboratory", "status": "ok"})


router = DefaultRouter()
router.register("orders", LabOrderViewSet, basename="lab-order")

urlpatterns = [
    path("health/", LaboratoryHealthAPIView.as_view(), name="health"),
    path("tests/", LabTestAPIView.as_view(), name="tests"),
    path("", include(router.urls)),
]
