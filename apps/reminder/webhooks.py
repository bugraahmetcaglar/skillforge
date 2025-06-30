from rest_framework.permissions import AllowAny
from rest_framework import status

from core.views import BaseAPIView
from core.services.telegram_api import TelegramReminderAPI


class TelegramReminderWebhookAPIView(BaseAPIView):
    """Webhook for Telegram Reminder Bot to receive messages."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = None

    def post(self, request, *args, **kwargs):
        """Handle incoming webhook messages from the Telegram Reminder Bot."""
        telegram_reminder = TelegramReminderAPI()
        breakpoint()
        data = {
            "update_id": 526592500,
            "message": {
                "message_id": 34,
                "from": {
                    "id": 1775999934,
                    "is_bot": False,
                    "first_name": "Orynex",
                    "username": "orynex",
                    "language_code": "en",
                },
                "chat": {"id": 1775999934, "first_name": "Orynex", "username": "orynex", "type": "private"},
                "date": 1751321883,
                "text": "sa",
            },
        }
        return self.success_response(data={"status": "success"}, status_code=status.HTTP_200_OK)
