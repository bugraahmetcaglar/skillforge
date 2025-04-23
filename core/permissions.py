from rest_framework import permissions

from apps.user.models import User


class IsOwnerOrAdmin(permissions.BasePermission):
    """Custom permission to only allow owners of an object or admins."""

    def has_object_permission(self, request, view, obj):
        user: User = request.user  # type: ignore

        if request.method in permissions.SAFE_METHODS:
            return user.is_staff or obj == user

        return False
