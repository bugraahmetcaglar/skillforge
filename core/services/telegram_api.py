from __future__ import annotations
import requests

from django.conf import settings


class TelegramAPI:
    """
    A class to interact with the Telegram Bot API.
    """

    BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    TELEGRAM_BOT_TOKEN = settings.TELEGRAM_REMINDER_BOT_TOKEN

    def __init__(self) -> None:
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram Bot Token is not set in settings.")

        # Initialize the base URL for the Telegram Bot API
        self.base_url = f"{self.BASE_URL}/bot{self.TELEGRAM_BOT_TOKEN}"

    def send_reminder_bot_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to a Telegram chat.

        :param chat_id: The ID of the chat to send the message to.
        :param text: The message text.
        :param parse_mode: The parse mode for formatting (default is HTML).
        :return: True if the message was sent successfully, False otherwise.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}

        response = requests.post(url, json=payload)

        return response.status_code == 200
