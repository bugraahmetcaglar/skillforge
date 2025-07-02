from __future__ import annotations
import logging

from rest_framework.permissions import AllowAny
from rest_framework import status

from core.views import BaseAPIView

logger = logging.getLogger(__name__)


class TelegramReminderWebhookAPIView(BaseAPIView):
    """Webhook for Telegram Reminder Bot to receive messages."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = None

    def post(self, request, *args, **kwargs):
        """Handle incoming webhook messages from the Telegram Reminder Bot."""
        webhook_data = request.data

        if "message" in webhook_data:
            message = webhook_data["message"]
            text = message.get("text", "")
            user_id = message["from"]["id"]
            chat_id = message["chat"]["id"]
            username = message["from"].get("username", "Unknown")

            logger.info(f"AI processing message from @{username}: {text}")

            # Process with NLP
            # processed_message = self.message_processor.process_message(text, user_id)

            # TODO: Execute appropriate task based on intent
            response_data = {
                "processed": {
                    "intent": processed_message.intent,
                    "confidence": processed_message.confidence,
                    "entities": processed_message.entities,
                    "original_text": processed_message.original_text,
                }
            }

            return self.success_response(
                data=response_data,
                message=f"AI processed message with intent: {processed_message.intent}",
                status_code=status.HTTP_200_OK,
            )
