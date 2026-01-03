from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    ChangePasswordView,
    AdminResetPasswordView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # --- Authentication ---
    path("auth/token/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),

    # --- User Management ---
    path("auth/register/", RegisterView.as_view(), name="register"),  # Admin only
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),  # Self
    path("auth/reset-password/", AdminResetPasswordView.as_view(), name="reset-password"),  # Admin only
]
