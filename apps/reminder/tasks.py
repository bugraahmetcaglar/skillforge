from datetime import date, timedelta
from django.db import models

from apps.contact.models import Contact
from apps.finance.enums import SubscriptionStatusChoices
from apps.finance.models import UserSubscription
from apps.reminder.services import send_telegram_message


def generate_birthday_reminders_in_30_days():
    today = date.today()
    end_date = today + timedelta(days=30)

    if today.year == end_date.year:
        contacts = Contact.objects.filter(
            models.Q(is_active=True, birthday__isnull=False)
            & (
                models.Q(birthday__month__gt=today.month)
                | models.Q(birthday__month=today.month, birthday__day__gte=today.day)
            )
            & (
                models.Q(birthday__month__lt=end_date.month)
                | models.Q(birthday__month=end_date.month, birthday__day__lte=end_date.day)
            )
        ).order_by("-birthday")

        for contact in contacts:
            message = "🎂 <b>Upcoming Birthdays:</b>\n\n"
            message += f"• {contact.display_name} - {contact.birthday.strftime("%d %B %Y")}\n"
        send_telegram_message(message)

    return True


def generate_auto_renewal_subscription_reminders():
    today = date.today()
    end_date = today + timedelta(days=7)
    user_subscriptions = UserSubscription.objects.filter(
        models.Q(is_active=True, auto_renewal=True, next_billing_date__isnull=False)
        & (
            models.Q(next_billing_date__month__gt=today.month)
            | models.Q(next_billing_date__month=today.month, next_billing_date__day__gte=today.day)
        )
        & (
            models.Q(next_billing_date__month__lt=end_date.month)
            | models.Q(next_billing_date__month=end_date.month, next_billing_date__day__lte=end_date.day)
        ),
        status=SubscriptionStatusChoices.ACTIVE,
    ).select_related("user", "service")

    for subscription in user_subscriptions:
        if subscription.user:
            message = "🔔 <b>Subscription Auto Renewal Reminder:</b>\n\n"
            message += f"• <b>Service:</b> {subscription.service.name}\n"
            message += f"• <b>Plan:</b> {subscription.plan_name}\n"
            message += f"• <b>Next Billing Date:</b> {subscription.next_billing_date.strftime('%d %B %Y')}\n"
            message += f"• <b>Amount:</b> {subscription.amount} {subscription.currency}\n"
            message += f"• <b>Website:</b> {subscription.service.website_url}\n"
            message += "\n"
        send_telegram_message(message)

    return True



def refresh_next_billing_dates():
    today = date.today()
    user_subscriptions = UserSubscription.objects.filter(
        next_billing_date__lt=today, status=SubscriptionStatusChoices.ACTIVE
    )

    for subscription in user_subscriptions:
        subscription.next_billing_date = subscription.next_billing_date + timedelta(days=30)
        subscription.save(update_fields=["next_billing_date"])

    return True