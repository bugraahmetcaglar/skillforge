from __future__ import annotations

from rest_framework import serializers

from apps.contact.models import Contact


class VCardUploadSerializer(serializers.Serializer):
    """Simple serializer for vCard file upload validation"""

    file = serializers.FileField(
        help_text="vCard file (.vcf format)",
        error_messages={
            "required": "Please provide a vCard file",
            "empty": "The uploaded file is empty",
            "invalid": "Invalid file format",
        },
    )

    def validate_file(self, file):
        """Validate uploaded vCard file"""
        # Check file extension
        if not file.name.endswith(".vcf"):
            raise serializers.ValidationError("Only .vcf files are allowed")

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB")

        # Basic content validation
        try:
            content = file.read()
            file.seek(0)  # Reset file pointer

            if isinstance(content, bytes):
                content = content.decode("utf-8")

            if "BEGIN:VCARD" not in content or "END:VCARD" not in content:
                raise serializers.ValidationError("Invalid vCard format")

        except UnicodeDecodeError:
            raise serializers.ValidationError(
                "File encoding error. Please ensure the file is UTF-8 encoded"
            )
        except Exception as e:
            raise serializers.ValidationError(f"Error validating file: {str(e)}")

        return file


class ContactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating individual contacts from parsed vCard data"""

    class Meta:
        model = Contact
        fields = ("first_name", "last_name", "email", "phone", "notes", "address")

    def validate_phone(self, value):
        """Validate and clean phone number"""
        if not value:
            raise serializers.ValidationError("Phone number is required")

        cleaned_phone = self._clean_phone_number(value)
        if not cleaned_phone or len(cleaned_phone) < 10:
            raise serializers.ValidationError("Invalid phone number format")

        return cleaned_phone

    def validate(self, attrs):
        """Validate that at least first_name or last_name is provided"""
        if not attrs.get("first_name") and not attrs.get("last_name"):
            raise serializers.ValidationError(
                "Either first name or last name is required"
            )

        return attrs

    def create(self, validated_data):
        """Create contact with owner from context"""
        user = self.context["user"]
        return Contact.objects.create(owner=user, **validated_data)

    def _clean_phone_number(self, phone: str) -> str:
        """Clean and normalize phone number"""
        if not phone:
            return ""

        import re

        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", phone.strip())

        # Handle Turkish phone number formats
        if cleaned.startswith("90") and len(cleaned) == 12:
            cleaned = "+" + cleaned
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = "+90" + cleaned[1:]
        elif not cleaned.startswith("+") and len(cleaned) == 10:
            cleaned = "+90" + cleaned
        elif cleaned.startswith("5") and len(cleaned) == 10:
            cleaned = "+90" + cleaned

        return cleaned
