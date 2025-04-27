from __future__ import annotations

from rest_framework import serializers

from apps.contact.models import Contact, ContactBackup


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "notes",
            "created_at",
            "last_updated",
        )
        read_only_fields = ("id", "created_at", "last_updated")

    def create(self, validated_data: dict) -> Contact:
        user = self.context["request"].user
        return Contact.objects.create(owner=user, **validated_data)


class ContactBackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactBackup
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "notes",
            "deactivated_at",
            "created_at",
        )
        read_only_fields = fields
