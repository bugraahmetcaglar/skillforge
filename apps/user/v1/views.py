from __future__ import annotations

import logging

from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User
from apps.user.serializers import UserLoginSerializer, UserSerializer, TokenSerializer
from core import views

logger = logging.getLogger(__name__)


class UserRegisterAPIView(views.BaseAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()

        return self.success_response(
            data=user.token(),
            message="User successfully registered",
            status_code=status.HTTP_201_CREATED,
        )


class UserListAPIView(views.BaseListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class UserDetailAPIView(views.BaseRetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class UserLoginAPIView(views.BaseCreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request=request, username=username, password=password)
        if not user:
            logger.error(f"Authentication failed for user: {username}")
            raise AuthenticationFailed("Invalid credentials.")

        refresh = RefreshToken.for_user(user)

        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return self.success_response(data=token_data)


class RegenerateTokenAPIView(APIView):
    """API view for regenerating authentication tokens"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = user.token()
        serializer = TokenSerializer(token)
        return Response(serializer.data, status=status.HTTP_200_OK)
