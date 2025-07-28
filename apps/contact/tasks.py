from __future__ import annotations

import logging

from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from apps.contact.models import Contact


logger = logging.getLogger(__name__)


@shared_task(bind=True, name="task_cleanup_inactive_contacts")
def task_cleanup_inactive_contacts(self) -> str:
    """Permanently delete contacts that have been inactive for more than 30 days."""

    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Get contacts to delete
    contacts_to_delete = Contact.objects.filter(is_active=False, deactivated_at__lt=thirty_days_ago)
    
    if not contacts_to_delete.exists():
        logger.info("No inactive contacts to delete.")
        return "No inactive contacts to delete."

    contacts_to_delete.delete()

    logger.info(f"Cleaned up inactive contacts")
    return f"Successfully deleted inactive contacts"


@shared_task(bind=True, name="task_save_contact")
def task_save_contact(self, contact_data: dict):
    """Save contact data to the database with optional photo processing.
    Args:
        contact_data (dict): Contact data to save, including photo information.
    Returns:
        bool: True if contact was saved successfully, False otherwise.
    """
    try:
        Contact.objects.create(**contact_data)
        return {"status": "success"}

    except Exception as err:
        logger.error(f"Failed to save contact: {err}")

        # Retry logic
        if self.request.retries < 3:
            logger.info(f"Retrying contact save task, attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, max_retries=3)

        return {"status": "failed", "error": str(err), "contact_data": contact_data}
