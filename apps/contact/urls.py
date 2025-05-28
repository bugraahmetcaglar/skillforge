from django.urls import path

from apps.contact.views import VCardImportAPIView, ContactListAPIView

urlpatterns = [
    path("import/vcard/", VCardImportAPIView.as_view(), name="vcard_import_api_view"),
    path("list/", ContactListAPIView.as_view(), name="contact_list_api_view"),
]
