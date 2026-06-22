from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appointments.services import get_available_slots

from .models import Doctor
from .serializers import DoctorSerializer


class IsAdminForWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, "role", None) == "ADMIN"


class DoctorViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Doctor.objects.select_related("department", "user").filter(is_active=True)
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "specialization", "department__name", "user__email"]
    ordering_fields = ["name", "specialization", "experience_yrs"]
    ordering = ["name"]


class DoctorAvailabilityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk, is_active=True)
        raw_date = request.GET.get("date")
        if not raw_date:
            return Response({"detail": "date is required in YYYY-MM-DD format."}, status=400)
        try:
            target_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)
        slots = [slot.strftime("%H:%M") for slot in get_available_slots(doctor, target_date)]
        return Response({"doctor_id": doctor.pk, "date": raw_date, "slots": slots})
