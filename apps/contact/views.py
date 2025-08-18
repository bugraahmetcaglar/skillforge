import logging
from typing import cast

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
    """API for importing contacts from VCard files"""

    serializer_class = VCardImportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Cast request.user to User type for type safety
        user = cast(User, request.user)
        try:
            service = VCardImportService(user=user, vcard_file=serializer.validated_data["vcard_file"])
            service.save_vcards()

            return self.success_response(
                message="Contacts will be processed in the background.", status_code=status.HTTP_202_ACCEPTED
            )
        except Exception as err:
            logger.error(f"Import error: {err}")
            return self.error_response(
                error_message="Failed to import contacts",
                status_code=status.HTTP_400_BAD_REQUEST,
                exception_msg=str(err),
            )


class ContactListAPIView(BaseListAPIView):
    """Contact List API with filtering and search"""

    serializer_class = ContactSerializer
    permission_classes = [IsOwner]
    filterset_class = ContactFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # type: ignore
    search_fields = ["first_name", "last_name", "email", "mobile_phone", "organization"]
    ordering_fields = ["created_at", "first_name", "last_name", "organization", "imported_at"]

    def get_queryset(self):
        logger.info(f"Fetching contacts for user {self.request.user.pk}")
        return Contact.objects.filter(user=self.request.user, is_active=True).select_related("user")


class ContactDetailAPIView(BaseRetrieveAPIView):
    """Contact Detail API - Get single contact with full information"""

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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]  # type: ignore

    def get(self, request: Request, *args, **kwargs) -> Response:
        _queryset = self.get_queryset()
        serializer = self.get_serializer(_queryset, many=True)

        if not serializer.data:
            return self.success_response(data=[], message="No duplicate contacts found")

        data = serializer.data
        if self.filterset_class:
            filterset = self.filterset_class(self.request.GET, queryset=_queryset)
            data = self.get_serializer(filterset.qs, many=True).data
        else:
            data = self.get_serializer(_queryset, many=True).data

        return self.success_response(
            data=data,
            message=f"Found {len(data)} duplicate contacts",
            status_code=status.HTTP_200_OK,
        )

    def get_queryset(self) -> models.QuerySet:
        """Get duplicate contacts using Contact manager's duplicate_numbers method"""
        logger.info(f"Fetching duplicate contacts for user {self.request.user.pk}")

        user: User | None = cast(User, self.request.user)

        if not user or not user.is_authenticated:
            return Contact.objects.none()

        _query_set = Contact.objects.duplicate_numbers(user_id=user.id)
        return _query_set
