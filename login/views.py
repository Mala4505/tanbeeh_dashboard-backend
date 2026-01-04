from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.generics import RetrieveAPIView

from .models import CustomUser
from .serializers import *
from attendance.models import AuditLog
from attendance.permissions import IsAdmin


class LoginView(APIView):
    """
    POST: Authenticate user and return access + refresh tokens + user info
    """
    def post(self, request):
        its_number = request.data.get("its_number")
        password = request.data.get("password")

        if not its_number or not password:
            return Response({"message": "ITS number and password required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate using Django's auth system
        user = authenticate(request, username=its_number, password=password)
        if user is None:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        # Audit log
        AuditLog.objects.create(
            user=user,
            action="login",
            target=str(user.id),
            metadata={"its_number": its_number}
        )

        # Build response payload
        user_data = {
            "id": str(user.id),
            "name": user.get_full_name() or user.username,
            "role": user.role,
            "its_number": user.its_number,
        }

        return Response({
            "access": access,
            "refresh": str(refresh),
            "user": user_data,
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    POST: Register a new user (Admin only)
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        username = request.data.get("username")
        its_number = request.data.get("its_number")
        password = request.data.get("password")
        role = request.data.get("role", "staff")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")

        if not username or not its_number or not password:
            return Response({"message": "username, its_number, and password are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(its_number=its_number).exists():
            return Response({"message": "User with this ITS number already exists"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create(
            username=username,
            its_number=its_number,
            password=make_password(password),
            role=role,
            first_name=first_name,
            last_name=last_name,
        )

        # Audit log
        AuditLog.objects.create(
            user=request.user,
            action="user_create",
            target=str(user.id),
            metadata={"created_username": username, "role": role}
        )

        return Response({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "its_number": user.its_number,
                "role": user.role,
                "name": user.get_full_name(),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    POST: Logout user by blacklisting their refresh token
    Body: { "refresh": "<refresh_token>" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"message": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Audit log
            AuditLog.objects.create(
                user=request.user,
                action="logout",
                target=str(request.user.id),
                metadata={"its_number": request.user.its_number}
            )

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    POST: Change own password
    Body: { "old_password": "...", "new_password": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"message": "Both old and new password required"}, status=400)

        user = request.user
        if not user.check_password(old_password):
            return Response({"message": "Old password incorrect"}, status=400)

        user.password = make_password(new_password)
        user.save()

        # Audit log
        AuditLog.objects.create(
            user=user,
            action="password_change",
            target=str(user.id),
            metadata={"changed_by": user.username}
        )

        return Response({"message": "Password changed successfully"}, status=200)


class AdminResetPasswordView(APIView):
    """
    POST: Admin resets another user's password
    Body: { "user_id": <id>, "new_password": "..." }
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        user_id = request.data.get("user_id")
        new_password = request.data.get("new_password")

        if not user_id or not new_password:
            return Response({"message": "user_id and new_password required"}, status=400)

        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        target_user.password = make_password(new_password)
        target_user.save()

        # Audit log
        AuditLog.objects.create(
            user=request.user,
            action="user_reset_password",
            target=str(target_user.id),
            metadata={"reset_by": request.user.username}
        )

        return Response({"message": f"Password reset successfully for {target_user.username}"}, status=200)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "its_number": getattr(user, "its_number", None),
            "name": getattr(user, "name", getattr(user, "username", None)),
            "role": getattr(user, "role", None),
        })
