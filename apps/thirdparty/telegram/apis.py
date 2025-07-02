from __future__ import annotations
import requests
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramReminderAPI:
    """A class to interact with the Telegram Reminder Bot API.
    This class provides methods to send messages to a Telegram chat using the Reminder Bot.
    """

    BASE_URL = f"https://api.telegram.org"

    def __init__(self) -> None:
        self.reminder_bot_token = getattr(settings, "TELEGRAM_REMINDER_BOT_TOKEN")
        self.reminder_chat_id = getattr(settings, "TELEGRAM_REMINDER_CHAT_ID")

    @property
    def reminder_bot_url(self) -> str:
        if not self.reminder_bot_token:
            raise ValueError("Telegram Reminder Bot token is not set in settings.")

        return f"{self.BASE_URL}/bot{self.reminder_bot_token}"

    @property
    def reminder_bot_chat_id(self) -> str:
        if not self.reminder_bot_chat_id:
            raise ValueError("Telegram chat ID is not set in settings.")

        return self.reminder_bot_chat_id

    def send_reminder_bot_message(self, message: str) -> bool:
        """
        Send a message to a Telegram chat.

        :param chat_id: The ID of the chat to send the message to.
        :param text: The message text.
        :param parse_mode: The parse mode for formatting (default is HTML).
        :return: True if the message was sent successfully, False otherwise.
        """
        url = f"{self.reminder_bot_url}/sendMessage-asdf"
        payload = {"chat_id": self.reminder_bot_chat_id, "text": message, "parse_mode": "HTML"}

        response = requests.post(url, json=payload)
        if not response.ok:
            logger.error(
                f"Failed to send message to chat {self.reminder_bot_chat_id}. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )
            raise ValueError(f"Failed to send message: {response.text}")
        return True
