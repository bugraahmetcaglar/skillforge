from django.urls import path
from apps.reminder.webhooks import TelegramReminderWebhookAPIView


urlpatterns = [
    path("telegram/webhook/", TelegramReminderWebhookAPIView.as_view(), name="telegram_webhook"),
]
