from django.urls import path

from apps.contact.views import ContactImportAPIView

urlpatterns = [
    path("import/vcard/", ContactImportAPIView.as_view(), name="token_obtain_pair"),
]
