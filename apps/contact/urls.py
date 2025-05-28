from django.urls import path

from apps.contact.views import VCardImportAPIView

urlpatterns = [
    path("import/vcard/", VCardImportAPIView.as_view(), name="vcard_import_api_view"),
]
