from django.urls import path

from apps.contact.views import (
    ContactDetailAPIView,
    VCardImportAPIView,
    ContactListAPIView,
    ContactDuplicateListAPIView,
)

urlpatterns = [
    path("import/vcard", VCardImportAPIView.as_view(), name="vcard_import_api_view"),
    path("list", ContactListAPIView.as_view(), name="contact_list_api_view"),
    path("duplicate-numbers/", ContactDuplicateListAPIView.as_view(), name="contact_duplicate_list_api_view"),
    path("detail/<int:pk>", ContactDetailAPIView.as_view(), name="contact_detail_api_view"),
]
