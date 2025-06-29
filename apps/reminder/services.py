import requests
import logging
from django.conf import settings


logger = logging.getLogger(__name__)


def send_telegram_message(message: str, chat_id: str | None = None) -> bool:
    """Send message to Telegram"""
    try:
        token = settings.TELEGRAM_REMINDER_BOT_TOKEN
        chat_id = chat_id or settings.TELEGRAM_CHAT_ID

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}  # HTML formatting için

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            logger.info(f"Telegram message sent successfully to {chat_id}")
            return True
        else:
            logger.error(f"Telegram API error: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False
