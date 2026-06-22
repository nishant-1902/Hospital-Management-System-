from rest_framework import filters, permissions, viewsets

from .models import Patient
from .serializers import PatientListSerializer, PatientSerializer


class IsAdminOrReceptionistForWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, "role", None) in {"ADMIN", "RECEPTIONIST"}


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReceptionistForWrite]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["pid", "name", "phone", "address", "user__email"]
    ordering_fields = ["name", "pid", "dob", "created_at", "updated_at"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        include_inactive = self.request.query_params.get("include_inactive")
        if include_inactive not in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PatientListSerializer
        return PatientSerializer
