from __future__ import annotations

from typing import Any
from rest_framework import serializers

from apps.contact.models import Contact, ContactBackup
from core.views import BaseRetrieveAPIView


class VCardImportSerializer(serializers.Serializer):
    vcard_file = serializers.FileField(help_text="vCard file (.vcf or .vcard)", allow_empty_file=False)

    def validate_vcard_file(self, value) -> Any:
        """Validate uploaded vCard file"""

        if not value.name.lower().endswith((".vcf", ".vcard")):
            raise serializers.ValidationError("Invalid file format. Please upload a .vcf or .vcard file.")

        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File too large. Maximum size is 5MB.")

        if value.size == 0:
            raise serializers.ValidationError("Empty file provided.")

        try:
            # TODO: Improve performance
            # Save current position
            current_position = value.tell()

            # Read content for validation
            content = value.read().decode("utf-8")

            # Reset file pointer
            value.seek(current_position)

            content_stripped = content.strip()
            if not content_stripped.startswith("BEGIN:VCARD"):
                raise serializers.ValidationError("Invalid vCard format. File must start with 'BEGIN:VCARD'.")

            if not content_stripped.endswith("END:VCARD"):
                raise serializers.ValidationError("Invalid vCard format. File must end with 'END:VCARD'.")

        except UnicodeDecodeError:
            raise serializers.ValidationError("Invalid file encoding. File must be UTF-8 encoded.")
        except Exception as e:
            raise serializers.ValidationError(f"Error reading file: {str(e)}")
        return value


class ContactListSerializer(serializers.ModelSerializer):

    display_name = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    contact_age = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        exclude = ("owner", "is_active", "deactivated_at", "external_id")

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


class ContactDetailSerializer(serializers.ModelSerializer):

    display_name = serializers.SerializerMethodField()
    contact_age = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        exclude = ["owner", "external_id"]

    def get_display_name(self, obj: Contact) -> str:
        """Get formatted display name"""
        if obj.full_name:
            return obj.full_name
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return "Unknown Contact"

    def get_contact_age(self, obj: Contact) -> int | None:
        """Calculate contact age if birthday exists"""
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
        exclude = ["id", "owner"]


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
