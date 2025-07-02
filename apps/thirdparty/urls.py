from django.urls import path

from apps.thirdparty.telegram.webhooks import TelegramReminderWebhookAPIView


urlpatterns = [
    path("telegram/webhook/", TelegramReminderWebhookAPIView.as_view(), name="telegram_webhook"),
]
