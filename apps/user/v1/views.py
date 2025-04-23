from __future__ import annotations

from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.request import Request

from apps.user.models import User
from apps.user.serializers import UserLoginSerializer, UserSerializer, TokenSerializer
from core import views


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

        breakpoint()
        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(Q(username=username) | Q(email=email)).first()
        if getattr(user, "is_active", False) is False:
            raise AuthenticationFailed("Invalid credentials.")

        user_auth = authenticate(username=user.username, password=password)
        if not user_auth:
            raise AuthenticationFailed("Invalid credentials.")

        return self.success_response(data=user.token())


class RegenerateTokenAPIView(APIView):
    """API view for regenerating authentication tokens"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = user.token()
        serializer = TokenSerializer(token)
        return Response(serializer.data, status=status.HTTP_200_OK)
