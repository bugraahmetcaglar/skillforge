from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from apps.user.models import User
from apps.user.serializers import UserSerializer, TokenSerializer


class UserRegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class UserListAPIView(ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class UserDetailAPIView(RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)


class RegenerateTokenAPIView(APIView):
    """API view for regenerating authentication tokens"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = user.token()
        serializer = TokenSerializer(token)
        return Response(serializer.data, status=status.HTTP_200_OK)
