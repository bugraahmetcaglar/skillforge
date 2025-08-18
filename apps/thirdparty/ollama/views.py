from __future__ import annotations

import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.thirdparty.ollama.services import OllamaService
from apps.thirdparty.ollama.serializers import OllamaStatusSerializer
from core.views import BaseAPIView

logger = logging.getLogger(__name__)


class OllamaHealthCheckAPIView(BaseAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = OllamaStatusSerializer

    def get(self, request, *args, **kwargs):
        try:
            service = OllamaService()
            status_data = service.health_check()

            # Validate response data with serializer
            serializer = self.get_serializer(data=status_data)
            serializer.is_valid(raise_exception=True)

            if status_data["status"] == "healthy":
                return self.success_response(data=serializer.validated_data, message="Ollama service is healthy")
            else:
                return self.error_response(
                    error_message="Ollama service is not healthy",
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        except Exception as err:
            logger.exception(f"Ollama status check failed: {err}")
            return self.error_response(
                error_message="Failed to check Ollama service status",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                exception_msg=str(err),
            )
