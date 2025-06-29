from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions

from core.permissions import IsOwner
from apps.user.models import User
from apps.user.serializers import TokenSerializer, UserSerializer, UserUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for the User model that consolidates CRUD operations in a single class.

    This ViewSet approach offers several advantages:
    1. Implement all CRUD operations with less code
    2. Automate URL routing using a router
    3. Define custom actions beyond standard CRUD operations

    ViewSets are particularly ideal for standard model operations.
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "register", "list"]:
            return UserSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ["create", "register"]:
            permission_classes = (permissions.AllowAny,)
        elif self.action == "list":
            permission_classes = (permissions.AllowAny,)
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsOwner]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True}, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=("post",),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def regenerate_token(self, request):
        user: User = request.user
        token = user.token()
        serializer = TokenSerializer(token)
        return Response(serializer.data, status=status.HTTP_200_OK)
