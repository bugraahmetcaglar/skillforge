import logging

from rest_framework import permissions

from apps.user.models import User
from rest_framework.request import Request


logger = logging.getLogger(__name__)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Custom permission to only allow owners of an object or admins."""

    def has_object_permission(self, request: Request, view, obj):
        try:
            user: User = request.user

            if user.is_staff:
                return True

            if hasattr(obj, "user"):
                return obj.user == user

            return obj == user
        except Exception as err:
            logger.exception(f"Permission check failed: {err}")
            return False


class IsOwner(permissions.BasePermission):
    """Custom permission to only allow owners of an object."""

    def has_object_permission(self, request: Request, view, obj):
        try:
            user: User = request.user

            if hasattr(obj, "user"):
                return obj.user == user

            return obj == user
        except Exception as err:
            logger.exception(f"Permission check failed: {err}")
            return False
