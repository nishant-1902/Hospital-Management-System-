from django.utils.deprecation import MiddlewareMixin

from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    ACTION_BY_METHOD = {
        "POST": AuditLog.CREATE,
        "PUT": AuditLog.UPDATE,
        "PATCH": AuditLog.UPDATE,
        "DELETE": AuditLog.DELETE,
    }

    def process_response(self, request, response):
        action = self.ACTION_BY_METHOD.get(request.method)
        if not action:
            return response

        user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
        ip_address = self.get_client_ip(request)

        try:
            AuditLog.objects.create(
                user=user,
                action=action,
                table_name=request.path[:50],
                details=f"{request.method} {request.path} returned {response.status_code}",
                ip_address=ip_address,
            )
        except Exception:
            pass

        return response

    def get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
