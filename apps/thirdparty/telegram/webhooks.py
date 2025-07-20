from __future__ import annotations
import logging

from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.thirdparty.telegram.serializers import TelegramWebhookSerializer
from core.views import BaseAPIView

logger = logging.getLogger(__name__)


class TelegramReminderWebhookAPIView(BaseAPIView):
    """Webhook for Telegram Reminder Bot to receive messages."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = TelegramWebhookSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle incoming webhook messages from the Telegram Reminder Bot."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        webhook_data = serializer.validated_data

        if "message" in webhook_data:
            message = webhook_data["message"]
            text = message.get("text", "")
            user_id = message["from"]["id"]
            # chat_id = message["chat"]["id"]
            username = message["from"].get("username", "Unknown")

            logger.info(f"Received message from user ID {user_id}: {text}")

            return self.success_response(status_code=status.HTTP_200_OK)
