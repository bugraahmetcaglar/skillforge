import logging

from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.views import BaseAPIView
from apps.contact.serializers import VCardUploadSerializer, ContactCreateSerializer
from apps.contact.utils.vcard_parser import VCardParser
from apps.contact.models import Contact


logger = logging.getLogger(__name__)


class ContactImportAPIView(BaseAPIView):
    """View for importing contacts from vCard files"""

    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Handle vCard file upload and import contacts"""

        # Step 1: Validate uploaded file
        upload_serializer = VCardUploadSerializer(data=request.FILES)
        if not upload_serializer.is_valid():
            logger.error(f"Serializer is not valid: {upload_serializer.errors}")
            return self.error_response(
                error_message=f"{upload_serializer.errors}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Step 2: Read and parse vCard file
            file = upload_serializer.validated_data["file"]
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")

            # Step 3: Parse vCard content
            parser = VCardParser()
            parsed_contacts = list(parser.parse_vcards(content))

            if not parsed_contacts:
                logger.error(f"No valid contacts found in the vCard file")
                return self.error_response(
                    error_message="No valid contacts found in the vCard file",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Step 4: Process each parsed contact
            contacts_created = []
            errors = []

            for contact_data in parsed_contacts:
                try:
                    # Step 5: Use serializer to create contact
                    contact_serializer = ContactCreateSerializer(
                        data=contact_data, context={"user": request.user}
                    )

                    if contact_serializer.is_valid():
                        contact = contact_serializer.save()
                        contacts_created.append(
                            {
                                "id": contact.id,
                                "name": f"{contact.first_name} {contact.last_name}".strip(),
                                "email": contact.email,
                                "phone": contact.phone,
                            }
                        )
                    else:
                        logger.error(f"Contact serializer is not valid: {contact_serializer.errors}")
                        errors.append(
                            {
                                "contact": self._get_display_name(contact_data),
                                "error": contact_serializer.errors,
                            }
                        )

                except Exception as e:
                    errors.append(
                        {
                            "contact": self._get_display_name(contact_data),
                            "error": str(e),
                        }
                    )

            # Step 6: Create response
            result = {
                "total_processed": len(parsed_contacts),
                "success_count": len(contacts_created),
                "error_count": len(errors),
                "contacts_created": contacts_created,
                "errors": errors,
            }

            # Create detailed response message
            success_msg = "Import completed successfully!"
            details = f"{result['success_count']} contacts created"

            if result["skipped_count"] > 0:
                details += f", {result['skipped_count']} skipped (duplicates)"

            if result["error_count"] > 0:
                details += f", {result['error_count']} failed"

            return self.success_response(
                data=result,
                message=f"{success_msg} {details}.",
                status_code=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return self.error_response(
                error_message=f"Import failed: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def _get_display_name(self, contact_data: dict) -> str:
        """Get display name for contact"""
        if contact_data.get("full_name"):
            return contact_data["full_name"]

        first_name = contact_data.get("first_name", "")
        last_name = contact_data.get("last_name", "")
        return f"{first_name} {last_name}".strip() or "Unknown"
