from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.doctors.models import Doctor

from .models import Appointment
from .serializers import AppointmentSerializer
from .services import get_available_slots
from .tasks import send_appointment_confirmation


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related("patient", "doctor").all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["patient", "doctor", "date", "status", "type"]
    search_fields = ["patient__name", "patient__pid", "doctor__name", "notes"]
    ordering_fields = ["date", "time", "created_at", "token_no"]
    ordering = ["-date", "-time"]

    def perform_create(self, serializer):
        doctor = serializer.validated_data["doctor"]
        date = serializer.validated_data["date"]
        token_no = (
            Appointment.objects.filter(doctor=doctor, date=date)
            .exclude(status=Appointment.CANCELLED)
            .count()
            + 1
        )
        appointment = serializer.save(token_no=token_no)
        send_appointment_confirmation.delay(appointment.pk)


class AvailableSlotsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        doctor_id = request.GET.get("doctor_id")
        raw_date = request.GET.get("date")
        if not doctor_id or not raw_date:
            return Response({"detail": "doctor_id and date are required."}, status=400)
        try:
            target_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)
        try:
            doctor = Doctor.objects.get(pk=doctor_id, is_active=True)
        except Doctor.DoesNotExist:
            return Response({"detail": "Doctor not found."}, status=404)
        slots = [slot.strftime("%H:%M") for slot in get_available_slots(doctor, target_date)]
        return Response({"doctor_id": doctor.pk, "date": raw_date, "slots": slots})
