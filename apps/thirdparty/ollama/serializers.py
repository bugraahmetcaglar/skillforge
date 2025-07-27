from __future__ import annotations

from rest_framework import serializers

from core.serializers import NullableCharSerializer


class OllamaStatusSerializer(serializers.Serializer):
    """Serializer for Ollama status response."""

    status = serializers.ChoiceField(choices=["healthy", "unhealthy", "unreachable", "timeout", "error"])
    ready_for_chat = serializers.BooleanField()
    available_models = serializers.ListField(child=serializers.CharField(), required=False)
    default_model = NullableCharSerializer()
    fallback_model = NullableCharSerializer()
    error = NullableCharSerializer()
