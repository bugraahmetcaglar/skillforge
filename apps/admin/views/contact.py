from django.http import HttpResponse

from apps.contact.models import Contact
from core.permissions import IsOwnerOrAdmin
from core.views import BaseListAPIView


class ContactListAPIView(BaseListAPIView):
    serializer_class = None
    queryset = Contact.objects.filter(is_active=True)
    permission_classes = [IsOwnerOrAdmin]
    