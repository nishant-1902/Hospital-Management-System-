from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from .views import JWTLoginView, JWTLogoutView, JWTTokenRefreshView


class AuthenticationHealthAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"app": "authentication", "status": "ok"})


urlpatterns = [
    path("health/", AuthenticationHealthAPIView.as_view(), name="health"),
    path("login/", JWTLoginView.as_view(), name="jwt-login"),
    path("logout/", JWTLogoutView.as_view(), name="jwt-logout"),
    path("token/refresh/", JWTTokenRefreshView.as_view(), name="jwt-token-refresh"),
]
