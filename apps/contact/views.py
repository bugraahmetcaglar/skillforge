import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework import filters
from rest_framework.request import Request
from rest_framework.response import Response

from apps.contact.filter import ContactDuplicateFilter, ContactFilter
from apps.contact.models import Contact
from apps.contact.serializers import (
    ContactSerializer,
    VCardImportSerializer,
    ContactDuplicateSerializer,
)
from apps.contact.services import VCardImportService
from core.permissions import IsOwner
from core.views import BaseAPIView, BaseListAPIView, BaseRetrieveAPIView

logger = logging.getLogger(__name__)


class VCardImportAPIView(BaseAPIView):
    serializer_class = VCardImportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = VCardImportService(user=request.user)
            results = service.import_from_file(serializer.validated_data["vcard_file"])

            return self.success_response(
                data=results,
                message=f"Imported {results['imported_count']} of {results['total_processed']} contacts",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return self.error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Import error: {e}")
            return self.error_response("Import failed", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactListAPIView(BaseListAPIView):
    """Contact List API with filtering and search

    Features:
    - Pagination
    - Advanced filtering (name, email, phone, organization, dates, etc.)
    - Full-text search across multiple fields
    - Ordering by various fields
    - Owner-based access control

    Query Parameters:
    - search: Global search across name, email, phone, organization
    - first_name, last_name: Filter by name (case-insensitive)
    - email: Filter by email (case-insensitive)
    - phone: Search in any phone field
    - organization, job_title, department: Organization filters
    - import_source: Filter by import source (google, outlook, vcard, etc.)
    - created_after, created_before: Date range filters
    - has_birthday, has_photo, has_notes: Boolean filters
    - tags: Filter by tag content
    - ordering: Sort by fields (created_at, first_name, last_name, etc.)

    Example URLs:
    - /api/v1/contact/list?search=john
    - /api/v1/contact/list?organization=google&has_birthday=true
    - /api/v1/contact/list?created_after=2024-01-01&ordering=-created_at
    """

    serializer_class = ContactSerializer
    permission_classes = [IsOwner]
    filterset_class = ContactFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "mobile_phone", "organization"]
    ordering_fields = ["created_at", "first_name", "last_name", "organization", "imported_at"]

    def get_queryset(self):
        logger.info(f"Fetching contacts for user {self.request.user.id}")
        return Contact.objects.filter(user=self.request.user, is_active=True).select_related("user")


class ContactDetailAPIView(BaseRetrieveAPIView):
    """Contact Detail API - Get single contact with full information

    Features:
    - Detailed contact information with formatted data
    - Calculated fields (age, display name, formatted phones)
    - Social media links formatting
    - Owner-based access control
    - Rich phone number presentation

    Returns:
    - All contact fields except sensitive data (user, external_id)
    - display_name: Formatted full name or fallback
    - contact_age: Calculated age from birthday

    URL: /api/v1/contact/<uuid:pk>/
    Method: GET
    """

    serializer_class = ContactSerializer
    permission_classes = [IsOwner]
    lookup_field = "pk"

    def get_queryset(self):
        """Get active contacts for the authenticated user only"""
        return Contact.objects.filter(user=self.request.user, is_active=True).select_related("user")

    def retrieve(self, request, *args, **kwargs):
        """Override to add custom response format and logging"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            # Log contact access for analytics (optional)
            logger.info(f"Contact {instance.id} accessed by user {request.user.id}")

            return self.success_response(
                data=serializer.data, message=f"Contact details for {serializer.data.get('display_name', 'Unknown')}"
            )

        except Contact.DoesNotExist:
            return self.error_response("Contact not found", status_code=status.HTTP_404_NOT_FOUND)


class ContactDuplicateListAPIView(BaseListAPIView):
    """Contact duplicate detection API using existing manager method"""

    serializer_class = ContactDuplicateSerializer
    permission_classes = [IsOwner]
    filterset_class = ContactDuplicateFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        """Get duplicate contacts using Contact manager's duplicate_numbers method"""
        logger.info(f"Fetching duplicate contacts for user {self.request.user.id}")

        return Contact.objects.duplicate_numbers(user=self.request.user)
