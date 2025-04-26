from django.utils import timezone
from django.db import models

from core.models import BaseModel
from apps.user.models import User


class Contact(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    deactivated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def deactivate(self) -> None:
        """Soft-delete the contact by marking it as inactive and recording the deactivation time."""
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save(update_fields=["is_active", "deactivated_at", "last_updated"])

        # Create a backup copy
        ContactBackup.objects.create(
            owner=self.owner,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
            email=self.email,
            phone=self.phone,
            address=self.address,
            notes=self.notes,
            birthday=self.birthday,
            deactivated_at=self.deactivated_at,
        )


class ContactBackup(BaseModel):
    """Backup model for storing deleted contacts."""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contact_backups"
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.middle_name} {self.last_name} (Backup)"
