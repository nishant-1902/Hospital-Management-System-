from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views import View
from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from .forms import LoginForm, PasswordResetConfirmForm, PasswordResetRequestForm, ProfileForm, ProfilePasswordChangeForm
from .tasks import send_password_reset_email


LOCKOUT_ATTEMPTS = 5
LOCKOUT_MINUTES = 30


ROLE_DASHBOARD_URLS = {
    "ADMIN": "/dashboard/admin/",
    "DOCTOR": "/dashboard/doctor/",
    "PATIENT": "/dashboard/patient/",
    "RECEPTIONIST": "/dashboard/reception/",
    "PHARMACIST": "/dashboard/pharmacy/",
    "LAB_TECH": "/dashboard/lab/",
}


def failed_attempts_key(email):
    return f"auth:failed:{email.lower()}"


def lockout_key(email):
    return f"auth:lockout:{email.lower()}"


def get_role_dashboard_url(user):
    return ROLE_DASHBOARD_URLS.get(user.role, "/")


def get_lockout_remaining(email):
    locked_until = cache.get(lockout_key(email))
    if not locked_until:
        return 0
    remaining = int((locked_until - timezone.now()).total_seconds())
    if remaining <= 0:
        cache.delete(lockout_key(email))
        cache.delete(failed_attempts_key(email))
        return 0
    return remaining


def register_failed_login(email):
    attempts_key = failed_attempts_key(email)
    attempts = cache.get(attempts_key, 0) + 1
    cache.set(attempts_key, attempts, LOCKOUT_MINUTES * 60)
    if attempts >= LOCKOUT_ATTEMPTS:
        locked_until = timezone.now() + timedelta(minutes=LOCKOUT_MINUTES)
        cache.set(lockout_key(email), locked_until, LOCKOUT_MINUTES * 60)
        return locked_until
    return None


def clear_failed_logins(email):
    cache.delete(failed_attempts_key(email))
    cache.delete(lockout_key(email))


class LoginView(View):
    template_name = "authentication/login.html"

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        email = form.cleaned_data["email"].strip().lower()
        password = form.cleaned_data["password"]
        remaining = get_lockout_remaining(email)

        if remaining:
            messages.error(request, f"Account locked. Try again in {remaining // 60 + 1} minutes.")
            return render(request, self.template_name, {"form": form, "lockout_remaining": remaining})

        user = authenticate(request, username=email, password=password)
        if user is None:
            locked_until = register_failed_login(email)
            if locked_until:
                messages.error(request, f"Too many failed attempts. Account locked for {LOCKOUT_MINUTES} minutes.")
                remaining = int((locked_until - timezone.now()).total_seconds())
                return render(request, self.template_name, {"form": form, "lockout_remaining": remaining})
            messages.error(request, "Invalid email or password.")
            return render(request, self.template_name, {"form": form})

        if not user.is_active:
            messages.error(request, "This account is inactive. Contact the administrator.")
            return render(request, self.template_name, {"form": form})

        clear_failed_logins(email)
        login(request, user)
        next_url = request.GET.get("next") or get_role_dashboard_url(user)
        return redirect(next_url)


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("authentication:login")

    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("authentication:login")


class PasswordResetRequestView(View):
    template_name = "authentication/password_reset.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PasswordResetRequestForm()})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(
                    reverse("authentication:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
                )
                send_password_reset_email.delay(user.email, reset_url)
            messages.success(request, "If that account exists, a password reset link has been sent.")
            return redirect("authentication:login")
        return render(request, self.template_name, {"form": form})


class PasswordResetConfirmView(View):
    template_name = "authentication/password_reset_confirm.html"

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user(kwargs["uidb64"])
        if self.user is None or not default_token_generator.check_token(self.user, kwargs["token"]):
            messages.error(request, "This password reset link is invalid or has expired.")
            return redirect("authentication:password_reset")
        return super().dispatch(request, *args, **kwargs)

    def get_user(self, uidb64):
        User = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def get(self, request, uidb64, token):
        return render(request, self.template_name, {"form": PasswordResetConfirmForm(self.user)})

    def post(self, request, uidb64, token):
        form = PasswordResetConfirmForm(self.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been reset. Please log in.")
            return redirect("authentication:login")
        return render(request, self.template_name, {"form": form})


class ProfileView(View):
    template_name = "authentication/profile.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to view your profile.")
            return redirect(f"{reverse('authentication:login')}?next={request.get_full_path()}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "profile_form": ProfileForm(instance=request.user),
                "password_form": ProfilePasswordChangeForm(request.user),
            },
        )

    def post(self, request):
        profile_form = ProfileForm(instance=request.user)
        password_form = ProfilePasswordChangeForm(request.user)

        if "update_profile" in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated.")
                return redirect("authentication:profile")

        if "change_password" in request.POST:
            password_form = ProfilePasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed.")
                return redirect("authentication:profile")

        return render(
            request,
            self.template_name,
            {"profile_form": profile_form, "password_form": password_form},
        )


class DashboardView(TemplateView):
    template_name = "authentication/dashboard.html"
    role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect(f"{reverse('authentication:login')}?next={request.get_full_path()}")
        if self.role and request.user.role != self.role:
            messages.error(request, "You do not have permission to access that dashboard.")
            return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dashboard_role"] = self.role
        return context


class JWTLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        return Response(
            {
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class JWTLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)


class JWTTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
