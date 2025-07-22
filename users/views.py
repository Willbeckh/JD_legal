from django.db import IntegrityError
from .models import User
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.exceptions import NotFound, ValidationError
from .permissions import IsAdmin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
)
from django.contrib.auth.password_validation import validate_password
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# class RegisterView(APIView):
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             # If using Token authentication previously, this would create a token:
#             # token = Token.objects.create(user=user)
#             return Response(
#                 {"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        data = request.data

        # Optional: Validate password strength manually
        try:
            validate_password(data.get("password"))
        except ValidationError as ve:
            return Response(
                {"password": ve.messages}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RegisterSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                return Response(
                    {
                        "message": "User registered successfully",
                        "user": UserSerializer(user).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
        except ValidationError as ve:
            logger.warning(f"Validation failed: {ve.detail}")
            return Response({"errors": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as ie:
            logger.error(f"Integrity error: {ie}")
            return Response(
                {
                    "error": "A user with provided credentials already exists.",
                    "detail": str(ie),
                },
                status=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            logger.exception("Unexpected error during registration")
            return Response(
                {"error": "An unexpected error occurred.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get(
            "refresh"
        )  # Use .get() to avoid KeyError if 'refresh' is missing
        if not refresh_token:
            raise ValidationError({"refresh": "Refresh token is required."})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {
                    "error": "Invalid token or token already blacklisted.",
                    "detail": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    lookup_field = "id"


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    lookup_field = "id"

    def perform_destroy(self, instance):
        """
        Performs a soft delete by setting is_active to False.
        If you intend a hard delete (remove from DB), remove the `is_active` line
        and keep `instance.delete()`.
        """
        instance.is_active = False  # For soft delete
        instance.save()

        # instance.delete() # For hard delete: uncomment

    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except Http404:
            raise NotFound("The user with the specified ID does not exist")

        self.perform_destroy(user)
        return Response(
            {"detail": "User deactivated (soft deleted)."},
            status=status.HTTP_204_NO_CONTENT,
        )
