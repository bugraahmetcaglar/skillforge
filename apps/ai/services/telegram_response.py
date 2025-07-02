from __future__ import annotations

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramResponseService:
    """Service for sending responses back to Telegram users"""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Send a text message to a Telegram chat"""

        url = f"{self.base_url}/sendMessage"

        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Message sent successfully to chat {chat_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def send_greeting(self, chat_id: int, first_name: str | None = None) -> bool:
        """Send greeting message"""

        greeting_text = "👋 Merhaba"
        if first_name:
            greeting_text += f" {first_name}"

        greeting_text += "!\n\nSize nasıl yardımcı olabilirim?"

        return self.send_message(chat_id, greeting_text)

    def send_help_menu(self, chat_id: int) -> bool:
        """Send help menu with available commands"""

        help_text = """🤖 <b>AI Asistan Yardım Menüsü</b>

                    📋 <b>Yapabileceklerim:</b>
                    - Gelecek ay abonelik masraflarınızı hesaplayabilirim
                    - Bu ay doğum günlerini listeleyebilirim
                    - Abonelik listelerinizi gösterebilirim

                    💬 <b>Örnek Mesajlar:</b>
                    - "gelecek ay abonelik tutar"
                    - "bu ay doğum günleri"
                    - "aboneliklerim listele"

                    💡 <b>İpucu:</b> "yardım" yazarak bu menüyü tekrar görebilirsiniz."""

        return self.send_message(chat_id, help_text)

    def send_unknown_intent(self, chat_id: int) -> bool:
        """Send message when intent is not recognized"""

        unknown_text = """🤔 Anlayamadım, tekrar anlatır mısınız?
                        <b>İpucu:</b> "yardım" yazarak neler yapabileceğimi öğrenebilirsiniz."""

        return self.send_message(chat_id, unknown_text)

    def send_processing_message(self, chat_id: int) -> bool:
        """Send processing message for long-running tasks"""

        processing_text = "⏳ İşleniyor... Lütfen bekleyin."

        return self.send_message(chat_id, processing_text)


class IntentResponseHandler:
    """Handle responses based on detected intents"""

    def __init__(self):
        self.telegram_service = TelegramResponseService()

    def handle_intent(self, intent: str, chat_id: int, user_id: int, username: str | None = None) -> bool:
        """Route intent to appropriate handler"""

        intent_handlers = {
            "greeting": self._handle_greeting,
            "help": self._handle_help,
            "subscription_next_month_cost": self._handle_subscription_cost,
            "unknown": self._handle_unknown,
        }

        handler = intent_handlers.get(intent, self._handle_unknown)
        return handler(chat_id, user_id, username)

    def _handle_greeting(self, chat_id: int, user_id: int, username: str | None = None) -> bool:
        """Handle greeting intent"""
        return self.telegram_service.send_greeting(chat_id, username)

    def _handle_help(self, chat_id: int, user_id: int, username: str | None = None) -> bool:
        """Handle help intent"""
        return self.telegram_service.send_help_menu(chat_id)

    def _handle_subscription_cost(self) -> None:
        """Handle subscription cost query"""
        from apps.reminder.tasks import monthly_subscription_expense_report

        monthly_subscription_expense_report.delay()

    def _handle_unknown(self, chat_id: int, user_id: int, username: str | None = None) -> bool:
        """Handle unknown intent"""
        return self.telegram_service.send_unknown_intent(chat_id)
