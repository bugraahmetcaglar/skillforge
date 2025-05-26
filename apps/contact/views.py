import logging

import logging
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.contact.serializers import VCardImportSerializer
from apps.contact.services.vcard_service import VCardImportService
from core.views import BaseAPIView

logger = logging.getLogger(__name__)


class VCardImportAPIView(BaseAPIView):
    serializer_class = VCardImportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = VCardImportService()
            results = service.import_from_file(
                serializer.validated_data["vcard_file"], request.user
            )

            return self.success_response(
                data=results,
                message=f"Imported {results['imported_count']} of {results['total_processed']} contacts",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return self.error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Import error: {e}")
            return self.error_response(
                "Import failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
