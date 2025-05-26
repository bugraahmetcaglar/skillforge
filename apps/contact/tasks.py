from __future__ import annotations

from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from apps.contact.models import Contact


@shared_task
def cleanup_inactive_contacts() -> str:
    """Permanently delete contacts that have been inactive for more than 30 days.

    The contacts are already backed up when they were deactivated, so this
    task just removes them from the main contacts table.

    This task should be scheduled to run periodically, e.g., once a day.

    Returns:
        str: Result message
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)

    Contact.objects.filter(
        is_active=False, deactivated_at__lt=thirty_days_ago
    ).delete()

    return "Success"
