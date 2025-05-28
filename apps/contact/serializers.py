from __future__ import annotations
from typing import Any

from rest_framework import serializers

from apps.contact.models import Contact


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


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        exclude = ("id",)
