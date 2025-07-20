import logging

from django.db import models
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
from apps.contact.vcard.services import VCardImportService
from apps.user.models import User
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

        service = VCardImportService(user=request.user)
        try:
            result = service.import_from_file(serializer.validated_data["vcard_file"])
            return self.success_response(
                data=result,
                message=f"Imported {result.get('imported_count', 0)} of {result.get('total_processed', 0)} contacts",
                status_code=status.HTTP_201_CREATED,
            )
        except ValueError as err:
            return self.error_response(str(err), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            logger.error(f"Import error: {err}")
            return self.error_response(f"Import error: {err}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter] # type: ignore
    search_fields = ["first_name", "last_name", "email", "mobile_phone", "organization"]
    ordering_fields = ["created_at", "first_name", "last_name", "organization", "imported_at"]

    def get_queryset(self):
        logger.info(f"Fetching contacts for user {self.request.user.pk}")
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter] # type: ignore

    def get_queryset(self) -> models.QuerySet:
        """Get duplicate contacts using Contact manager's duplicate_numbers method"""
        logger.info(f"Fetching duplicate contacts for user {self.request.user.pk}")

        user_id = self.request.user.pk
        if not user_id:
            return Contact.objects.none()
        return Contact.contact_manager.duplicate_numbers(user_id=user_id)
    