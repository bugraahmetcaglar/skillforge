from django.urls import path

from apps.thirdparty.telegram.webhooks import TelegramReminderWebhookAPIView


urlpatterns = [
    # Telegram webhook
    path("webhook/", TelegramReminderWebhookAPIView.as_view(), name="telegram_webhook"),
]
