from __future__ import annotations
import datetime

from django.forms.models import model_to_dict
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.enums import SourceTextChoices
from core.fields import NullableCharField
from core.models import BaseModel
from apps.user.models import User


class Contact(BaseModel):
    """Model for storing contact information imported from various sources."""

    # Relationship to the user who owns this contact
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")

    # Basic information
    first_name = NullableCharField()
    middle_name = NullableCharField()
    last_name = NullableCharField()
    full_name = NullableCharField()
    nickname = NullableCharField()

    # Contact information
    email = NullableCharField()
    emails = models.JSONField(default=list, blank=True)
    phones = models.JSONField(default=list, blank=True)
    mobile_phone = NullableCharField(max_length=16)
    home_phone = NullableCharField(max_length=16)
    work_phone = NullableCharField(max_length=16)
    second_phone = NullableCharField(max_length=16)
    third_phone = NullableCharField(max_length=16)
    addresses = models.JSONField(
        default=list, blank=True
    )  # List of addresses with labels

    # Company information
    organization = NullableCharField()
    job_title = NullableCharField()
    department = NullableCharField()

    # Personal information
    birthday = models.DateField(null=True, blank=True)
    anniversary = models.DateField(null=True, blank=True)

    # Online presence
    websites = models.JSONField(default=list, blank=True)
    social_profiles = models.JSONField(default=dict, blank=True)

    # Notes
    notes = models.TextField(null=True, blank=True)

    # Import metadata: google, outlook, vcard, etc.
    import_source = models.CharField(
        max_length=50,
        choices=SourceTextChoices.choices,
        default=SourceTextChoices.MANUAL,
    )
    # ID from the source system
    external_id = NullableCharField()
    imported_at = models.DateTimeField(auto_now_add=True)

    # Tags for categorization
    tags = models.JSONField(default=list, blank=True)

    # Photo
    photo_url = models.URLField(blank=True, default="")

    deactivated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner", "full_name"]),
            models.Index(fields=["import_source"]),
        ]
        unique_together = [["owner", "external_id", "import_source"]]
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or "Unnamed Contact"

    def deactivate(self) -> None:
        """Soft-delete the contact by marking it as inactive and recording the deactivation time."""
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save(update_fields=["is_active", "deactivated_at", "last_updated"])

        # Create a backup copy
        ContactBackup.objects.create(
            contact_id=str(self.pk),
            owner=self.owner,
            contact_data=model_to_dict(self),
        )

    @classmethod
    def search(cls, owner: User, query: str) -> models.QuerySet:
        """Search contacts by name, email, phone, etc."""
        return cls.objects.filter(
            owner=owner,
            is_active=True,
        ).filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(mobile_phone__icontains=query)
            | Q(organization__icontains=query)
            | Q(job_title__icontains=query)
        )


class ContactBackup(BaseModel):
    """Backup model for storing deleted contacts."""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contact_backups"
    )
    contact_data = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def delete(self):
        self.is_active = False
        self.save(update_fields=["is_active", "last_updated"])

    def restore(self) -> Contact:
        """Restore the contact from backup."""
        data = self.contact_data.copy()

        # Extract fields that need special handling
        birthday = data.pop("birthday", None)
        if birthday:
            data["birthday"] = timezone.datetime.fromisoformat(birthday).date()

        anniversary = data.pop("anniversary", None)
        if anniversary:
            data["anniversary"] = timezone.datetime.fromisoformat(anniversary).date()

        # Remove timestamp fields
        data.pop("imported_at", None)
        data.pop("deactivated_at", None)

        # Create new contact
        contact = Contact.objects.create(owner=self.owner, **data)
        return contact
