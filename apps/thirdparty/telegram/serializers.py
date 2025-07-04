from __future__ import annotations

from rest_framework import serializers


class TelegramWebhookSerializer(serializers.Serializer):
    """Serializer for incoming Telegram webhook data"""

    update_id = serializers.IntegerField()
    message = serializers.DictField()

    def validate_message(self, value):
        """Validate message structure"""
        required_fields = ["message_id", "from", "chat", "date"]

        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")

        # Validate 'from' field
        from_data = value.get("from", {})
        if "id" not in from_data:
            raise serializers.ValidationError("Missing user ID in 'from' field")

        # Validate 'chat' field
        chat_data = value.get("chat", {})
        if "id" not in chat_data:
            raise serializers.ValidationError("Missing chat ID in 'chat' field")

        return value


class ProcessedMessageSerializer(serializers.Serializer):
    """Serializer for AI processed message response"""

    intent = serializers.CharField(allow_null=True)
    confidence = serializers.FloatField()
    entities = serializers.DictField()
    original_text = serializers.CharField()
    pattern_id = serializers.IntegerField(allow_null=True)


class AIWebhookResponseSerializer(serializers.Serializer):
    """Serializer for AI webhook response"""

    processed = ProcessedMessageSerializer()
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
