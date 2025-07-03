from __future__ import annotations
import logging

from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.ai.nlp.message_processor import TelegramMessageProcessor
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
        self.message_processor = TelegramMessageProcessor()

    def post(self, request, *args, **kwargs):
        """Handle incoming webhook messages from the Telegram Reminder Bot."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        webhook_data = serializer.validated_data

        if "message" in webhook_data:
            message = webhook_data["message"]
            text = message.get("text", "")
            user_id = message["from"]["id"]
            chat_id = message["chat"]["id"]
            print(chat_id)
            username = message["from"].get("username", "Unknown")

            logger.info(f"AI processing message from @{username}: {text}")

            # Process with NLP
            processed_message = self.message_processor.process_message(message_text=text, user_id=user_id)

            # Handle intent and send response
            from apps.ai.services.telegram_response import IntentTelegramResponseHandler

            intent_handler = IntentTelegramResponseHandler()
            intent_handler.handle_intent(intent=processed_message.intent)
            response_data = {
                "processed": {
                    "intent": processed_message.intent,
                    "confidence": processed_message.confidence,
                    "entities": processed_message.entities,
                    "original_text": processed_message.original_text,
                }
            }

            logger.info(
                f"Processed message: intent={processed_message.intent}, "
                f"confidence={processed_message.confidence}, entities={processed_message.entities}"
            )

            return self.success_response(
                data=response_data,
                message=f"AI processed message with intent: {processed_message.intent}",
                status_code=status.HTTP_200_OK,
            )
