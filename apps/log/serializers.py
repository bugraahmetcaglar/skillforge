from rest_framework import serializers
from apps.log.models import LogEntry


class LogEntrySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()
    short_message = serializers.SerializerMethodField()
    has_exception = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "timestamp",
            "formatted_timestamp",
            "level",
            "message",
            "short_message",
            "logger_name",
            "module",
            "function_name",
            "user_username",
            "request_path",
            "status_code",
            "app_name",
            "has_exception",
        ]

    def get_formatted_timestamp(self, obj) -> str:
        return obj.timestamp.strftime("%Y-%M-%d %H:%M:%S")

    def get_short_message(self, obj) -> str:
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message

    def get_has_exception(self, obj) -> bool:
        return bool(obj.exception_info)


class LogSearchSerializer(serializers.Serializer):
    """Serializer for log search requests"""

    q = serializers.CharField(required=False, allow_blank=True, max_length=500)
    level = serializers.ChoiceField(
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], required=False, allow_blank=True
    )
    hours = serializers.IntegerField(required=False, default=24, min_value=1, max_value=168)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    limit = serializers.IntegerField(required=False, default=100, min_value=1, max_value=1000)
