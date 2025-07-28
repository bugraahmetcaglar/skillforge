from __future__ import annotations

import logging
from typing import Any
from rest_framework import serializers

from apps.contact.models import Contact

logger = logging.getLogger(__name__)


class VCardImportSerializer(serializers.Serializer):
    vcard_file = serializers.FileField(help_text="vCard file (.vcf or .vcard)", allow_empty_file=False)

    def validate_vcard_file(self, value):
        if not hasattr(value, "name"):  # Ensure the file has a name attribute
            raise serializers.ValidationError("Invalid file format. File must have a name.")

        if not value.name.lower().endswith((".vcf", ".vcard")):
            raise serializers.ValidationError("Invalid file format. Please upload a .vcf or .vcard file.")

        if value.size == 0:
            raise serializers.ValidationError("Empty file provided.")

        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("File too large. Maximum size is 5MB.")

        if not hasattr(value, "read"):
            raise serializers.ValidationError("Invalid file format. File must be readable.")

        return value


class ContactSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    contact_age = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        exclude = ("user", "is_active", "deactivated_at", "external_id")

    def get_display_name(self, obj: Contact) -> str:
        if obj.full_name:
            return obj.full_name
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        if obj.email:
            return obj.email
        return "Unknown Contact"

    def get_primary_phone(self, obj: Contact) -> str | None:
        return obj.mobile_phone or obj.home_phone or obj.work_phone

    def get_contact_age(self, obj: Contact) -> int | None:
        if not obj.birthday:
            return None

        from datetime import date

        today = date.today()
        return today.year - obj.birthday.year - ((today.month, today.day) < (obj.birthday.month, obj.birthday.day))


class ContactBackupCreateSerializer(serializers.ModelSerializer):
    """ModelSerializer for creating new contacts"""

    external_id = serializers.CharField(read_only=True)
    import_source = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        exclude = ["id", "user"]


class ContactDuplicateSerializer(serializers.ModelSerializer):
    """ModelSerializer for duplicate contact detection results from manager queryset"""

    # These fields come from window annotations in manager
    contact_rank = serializers.IntegerField(read_only=True)
    duplicate_count = serializers.IntegerField(read_only=True)

    # Additional computed fields
    is_primary = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            "id",
            "mobile_phone",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "created_at",
            "import_source",
            "contact_rank",
            "duplicate_count",
            "display_name",
            "is_primary",
        ]

    def get_is_primary(self, obj: dict) -> bool:
        """Check if this is the primary contact (rank 1 = oldest)"""

        return obj.get("contact_rank", 0) == 1
