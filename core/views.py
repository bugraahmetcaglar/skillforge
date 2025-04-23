from __future__ import annotations

import logging
from typing import Any, Type

from django.conf import settings
from rest_framework.exceptions import (
    NotFound,
    ValidationError,
    PermissionDenied,
    AuthenticationFailed,
    MethodNotAllowed,
)
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict[str, Any]):
    """Custom exception handler that masks errors in production for security"""
    response = drf_exception_handler(exc, context)

    generic_exceptions: dict[Type[Exception], int] = {
        NotFound: status.HTTP_404_NOT_FOUND,
        PermissionDenied: status.HTTP_403_FORBIDDEN,
        AuthenticationFailed: status.HTTP_401_UNAUTHORIZED,
        MethodNotAllowed: status.HTTP_405_METHOD_NOT_ALLOWED,
        ValidationError: status.HTTP_400_BAD_REQUEST,
    }

    if not settings.DEBUG:
        if response is not None:
            exc_class = exc.__class__

            if exc_class in generic_exceptions:
                response.data = {"detail": "Invalid request."}
        else:
            # Handle non-DRF exceptions
            logger = logging.getLogger(__name__)
            logger.error(f"Exception: {exc}", exc_info=True)

            response = Response(
                {"detail": "Invalid request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return response


class BaseAPIView(GenericAPIView):
    """BaseAPIView: Core foundation for standardized API responses and error handling.

    Features:
    - Consistent response formatting across all API endpoints
    - Integrated logging with appropriate severity levels
    - Environment-aware error handling (detailed in dev, sanitized in production)
    - OWASP-compliant security measures
    - Success/error response helpers with standardized structure

    Parent class for specialized views (BaseListAPIView, BaseCreateAPIView, etc.)
    that follow SOLID principles while maintaining uniform API behavior.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def success_response(
        self,
        data: dict | list | None = None,
        status_code: int = 200,
        message: str | None = None,
    ) -> Response:
        response_data = {"success": True}

        if message:
            response_data["message"] = message  # type: ignore

        if data is not None:
            response_data["data"] = data  # type: ignore

        return Response(response_data, status=status_code)

    def error_response(
        self,
        error_message: str = "",
        error_code: str | None = None,
        status_code: int = 400,
    ) -> Response:
        response_data = {"success": False, "detail": error_message}

        if error_code and settings.DEBUG:
            response_data["code"] = error_code

        return Response(response_data, status=status_code)


class BaseListAPIView(mixins.ListModelMixin, BaseAPIView):
    """API view for listing model instances"""

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BaseCreateAPIView(mixins.CreateModelMixin, BaseAPIView):
    """API view for creating a model instance"""

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return self.success_response(
            status_code=status.HTTP_201_CREATED, message="Resource created successfully"
        )


class BaseRetrieveAPIView(mixins.RetrieveModelMixin, BaseAPIView):
    """API view for retrieving a model instance"""

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(data=serializer.data)


class BaseUpdateAPIView(mixins.UpdateModelMixin, BaseAPIView):
    """API view for updating a model instance"""

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return self.success_response(
            data=serializer.data, message="Resource updated successfully"
        )
