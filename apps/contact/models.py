from __future__ import annotations

from django.forms.models import model_to_dict
from django.db import models
from django.db.models.functions import RowNumber
from django.utils import timezone as django_timezone

from core.enums import SourceTextChoices
from core.fields import NullableCharField
from core.models import BaseModel
from apps.user.models import User


class ContactManager(models.Manager):
    def duplicate_numbers(self, owner: User) -> models.QuerySet:
        """Find duplicate phone numbers with details"""

        duplicate_numbers = (
            self.filter(owner=owner, is_active=True, mobile_phone__isnull=False)
            .exclude(mobile_phone="")
            .annotate(
                # Count duplicates for each mobile phone number
                phone_count=models.Window(expression=models.Count("mobile_phone"), partition_by=["mobile_phone"]),
                # Rank by creation date (1 = primary/oldest)
                contact_rank=models.Window(
                    expression=RowNumber(), partition_by=["mobile_phone"], order_by=["created_at"]
                ),
            )
            .filter(phone_count__gt=1)
            .values(
                "mobile_phone",
                "contact_rank",
                "id",
                "first_name",
                "middle_name",
                "last_name",
                "import_source",
                "email",
                "created_at",
            )
            .order_by("-created_at")
        )
        return duplicate_numbers


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
    addresses = models.JSONField(default=list, blank=True)  # List of addresses with labels

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

    objects = ContactManager()

    class Meta:
        unique_together = [["owner", "external_id", "import_source"]]
        ordering = ["first_name", "middle_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or "Unnamed Contact"

    def delete(self) -> None:
        """Soft-delete the contact by marking it as inactive and recording the deactivation time."""
        self.is_active = False
        self.deactivated_at = django_timezone.now()
        self.save(update_fields=["is_active", "deactivated_at", "last_updated"])

        # Create a backup copy
        ContactBackup.objects.create(
            contact_id=str(self.pk),
            owner=self.owner,
            contact_data=model_to_dict(self),
        )

    @classmethod
    def search(cls, owner: User, keyword: str) -> models.QuerySet:
        return cls.objects.filter(
            owner=owner,
            is_active=True,
        ).filter(
            models.Q(first_name__icontains=keyword)
            | models.Q(last_name__icontains=keyword)
            | models.Q(email__icontains=keyword)
            | models.Q(mobile_phone__icontains=keyword)
        )

    @property
    def display_name(self, obj: Contact) -> str:
        """Get formatted display name"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name or ''} {obj.middle_name or ''} {obj.last_name or ''}".strip()
        return "Unknown Contact"


class ContactBackup(BaseModel):
    """Backup model for storing deleted contacts."""

    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        related_name="backups",
        db_constraint=False,
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contact_backups",
    )
    contact_data = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def delete(self) -> bool:
        self.is_active = False
        self.save(update_fields=["is_active", "last_updated"])
        return True

    def restore(self) -> Contact:
        """Restore the contact from backup."""
        self.contact.is_active = True
        self.contact.save(update_fields=["is_active", "last_updated"])

        # Mark the backup as inactive
        self.delete()

        return self.contact
