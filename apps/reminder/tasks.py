from datetime import date, timedelta
from decimal import Decimal
from django.db import models

from apps.contact.models import Contact
from apps.finance.enums import SubscriptionStatusChoices
from apps.finance.models import UserSubscription
from apps.thirdparty.telegram.apis import TelegramReminderAPI
from core.enums import CurrencyChoices
from core.services.exchange_rate_api import ExchangeRateAPI


def generate_birthday_reminders_in_30_days():
    """Generates reminders for contacts with upcoming birthdays in the next 30 days
    and sends them via Telegram."""
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
        TelegramReminderAPI().send_reminder_bot_message(message)

    return True


def generate_auto_renewal_subscription_reminders():
    """Generates reminders for user subscriptions that are set to auto-renew
    within the next 7 days and sends them via Telegram."""
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

    message = "🔔 <b>Subscription Auto Renewal Reminder:</b>\n\n"
    for subscription in user_subscriptions:
        if subscription.user:
            message += f"• <b>Service:</b> {subscription.service.name}\n"
            message += f"• <b>Plan:</b> {subscription.plan_name}\n"
            message += f"• <b>Next Billing Date:</b> {subscription.next_billing_date.strftime('%d %B %Y')}\n"
            message += f"• <b>Amount:</b> {subscription.amount} {subscription.currency}\n"
            message += f"• <b>Website:</b> {subscription.service.website_url}\n"
            message += "\n"

    TelegramReminderAPI().send_reminder_bot_message(message)

    return True


def refresh_next_billing_dates():
    """Refreshes the next billing dates for all active user subscriptions
    that have a next billing date in the past.
    """
    today = date.today()
    user_subscriptions = UserSubscription.objects.filter(
        next_billing_date__lt=today, status=SubscriptionStatusChoices.ACTIVE
    )

    for subscription in user_subscriptions:
        subscription.next_billing_date = subscription.next_billing_date + timedelta(days=30)
        subscription.save(update_fields=["next_billing_date", "last_updated"])

    return True


def monthly_subscription_expense_report():
    """Generates a monthly subscription expense report and sends it via Telegram."""
    today = date.today()
    start_date = today.replace(day=1)
    end_date = (start_date + timedelta(days=31)).replace(day=1)

    user_subscriptions = UserSubscription.objects.filter(
        next_billing_date__gte=start_date, next_billing_date__lt=end_date, status=SubscriptionStatusChoices.ACTIVE
    )

    total_amount = Decimal("0.00")
    for user_subscription in user_subscriptions:
        conversion_rate = Decimal("1.00")

        if user_subscription.currency != CurrencyChoices.TRY:
            conversion_rate = ExchangeRateAPI().get_exchange_rate(
                base_currency=user_subscription.currency,
                target_currency=CurrencyChoices.TRY,
            )

        total_amount += user_subscription.amount * conversion_rate

    message = "💰 <b>This Month's Subscription Amount:</b>\n\n"
    message += f"• <b>Total Amount:</b> {total_amount} 'TRY'\n"
    message += "\n"
    TelegramReminderAPI().send_reminder_bot_message(message)

    return "succesfull"


def next_month_subscription_expense_report():
    """Generates a next month's subscription expense report and sends it via Telegram."""
    today = date.today()
    message = "💰 <b>This Month's Subscription Amount:</b>\n\n"

    if today.month == 12:
        start_date = date(year=today.year + 1, month=1, day=1)
        end_date = date(year=today.year + 1, month=2, day=1)
        message += "<b>Don't forget to check new year prices !</b>\n\n"
    else:
        start_date = date(year=today.year, month=today.month + 1, day=1)
        end_date = date(year=today.year, month=today.month + 2, day=1)

    user_subscriptions = UserSubscription.objects.filter(
        next_billing_date__gte=start_date, next_billing_date__lt=end_date, status=SubscriptionStatusChoices.ACTIVE
    )

    total_amount = Decimal("0.00")
    for user_subscription in user_subscriptions:
        conversion_rate = Decimal("1.00")

        if user_subscription.currency != CurrencyChoices.TRY:
            conversion_rate = ExchangeRateAPI().get_exchange_rate(
                base_currency=user_subscription.currency,
                target_currency=CurrencyChoices.TRY,
            )

        total_amount += user_subscription.amount * conversion_rate

    message += f"• <b>Total Amount:</b> {total_amount} 'TRY'\n"
    message += "\n"
    TelegramReminderAPI().send_reminder_bot_message(message)

    return "succesfull"
