from __future__ import annotations
import logging

from apps.thirdparty.telegram.apis import TelegramReminderAPI


logger = logging.getLogger(__name__)


class TelegramResponseService(TelegramReminderAPI):
    """Service for sending responses back to Telegram users"""

    def send_greeting(self, first_name: str | None = None) -> bool:
        """Send greeting message"""

        greeting_text = "👋 Merhaba"
        if first_name:
            greeting_text += f" {first_name}"

        greeting_text += "!\n\nSana nasıl yardımcı olabilirim?"

        return self.send_message(greeting_text)

    def send_help_menu(self) -> bool:
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

        return self.send_message(help_text)

    def send_unknown_intent(self) -> bool:
        """Send message when intent is not recognized"""

        unknown_text = """🤔 Anlayamadım, tekrar anlatır mısınız?
                        <b>İpucu:</b> "yardım" yazarak neler yapabileceğimi öğrenebilirsiniz."""

        return self.send_message(unknown_text)

    def send_processing_message(self) -> bool:
        """Send processing message for long-running tasks"""

        return self.send_message("⏳ İşleniyor... Lütfen bekleyin.")
