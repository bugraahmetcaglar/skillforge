from __future__ import annotations

import logging

from django.conf import settings
from rest_framework.exceptions import NotFound

from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Custom exception handler that masks errors in production for security"""
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Mask specific errors in production
        if not settings.DEBUG and isinstance(exc, NotFound):
            response.data = {"detail": "Invalid request."}
    else:
        # Handle non-DRF exceptions
        if not settings.DEBUG:
            logger = logging.getLogger(__name__)
            logger.error(f"Unhandled exception: {exc}", exc_info=True)

            # Return generic error in production
            response = Response(
                {"detail": "An unexpected error occured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return response


class BaseAPIView(GenericAPIView):
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
            response_data["message"] = message

        if data is not None:
            response_data["data"] = None

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
