from django.urls import path
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Medicine


class MedicineAutocompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get("q", "").strip()
        medicines = Medicine.objects.filter(is_active=True)
        if query:
            medicines = medicines.filter(name__icontains=query) | medicines.filter(generic_name__icontains=query)
        results = [
            {
                "id": medicine.pk,
                "name": medicine.name,
                "generic_name": medicine.generic_name,
                "label": f"{medicine.name} ({medicine.generic_name})",
                "stock": medicine.quantity,
                "unit": medicine.unit,
            }
            for medicine in medicines.distinct().order_by("name")[:25]
        ]
        return Response({"results": results})


class PharmacyHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "pharmacy", "status": "ok"})


urlpatterns = [
    path("health/", PharmacyHealthAPIView.as_view(), name="health"),
    path("medicines/", MedicineAutocompleteAPIView.as_view(), name="medicines"),
]
