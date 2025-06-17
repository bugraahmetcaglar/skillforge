from datetime import date, timedelta
from django.db import models

from apps.contact.models import Contact
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
