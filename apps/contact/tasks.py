from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone
from django_q.tasks import async_task, schedule
from django_q.models import Schedule

from apps.contact.enums import SourceEnum
from apps.contact.models import Contact
from apps.contact.utils import generate_external_id
from apps.user.models import User

logger = logging.getLogger(__name__)


def cleanup_inactive_contacts() -> str:
    """Permanently delete contacts that have been inactive for more than 30 days.

    The contacts are already backed up when they were deactivated, so this
    task just removes them from the main contacts table.

    Returns:
        str: Result message with count of deleted contacts
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Get contacts to delete
    contacts_to_delete = Contact.objects.filter(is_active=False, deactivated_at__lt=thirty_days_ago)

    count = contacts_to_delete.count()
    contacts_to_delete.delete()

    logger.info(f"Cleaned up {count} inactive contacts")
    return f"Successfully deleted {count} inactive contacts"


# Background task for saving contacts
def save_contacts_task(user_id: int, contacts: list[dict]) -> dict[str, Any]:
    """Background task to save contacts to database

    Args:
        user_id: ID of the user who owns the contacts
        contacts: List of contact data dictionaries

    Returns:
        dict: Import results with counts and errors
    """
    try:
        user = User.objects.get(id=user_id)

        imported_count = 0
        failed_count = 0
        errors = []

        for i, data in enumerate(contacts):
            try:
                data.update({"owner": user, "import_source": "vcard"})

                # Skip completely empty contacts
                if not any(data.get(f) for f in ["first_name", "last_name", "full_name", "email", "mobile_phone"]):
                    failed_count += 1
                    continue

                # Generate external_id from mobile phone
                data["external_id"] = generate_external_id(
                    data=f"{data.get('mobile_phone', '')}", source=SourceEnum.VCARD.value
                )

                Contact.objects.create(**data)
                imported_count += 1

            except Exception as err:
                logger.exception(f"Failed to save contact {i+1} for user {user_id}: {err}")
                failed_count += 1
                errors.append(f"Contact {i+1}: {str(err)}")

        result = {
            "imported_count": imported_count,
            "failed_count": failed_count,
            "total_processed": len(contacts),
            "errors": errors,
            "user_id": user_id,
        }

        logger.info(f"Contact import completed for user {user_id}: {result}")
        return result

    except User.DoesNotExist:
        error_msg = f"User with ID {user_id} not found"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        logger.error(f"Contact saving task failed for user {user_id}: {e}")
        raise


def save_contacts_hook(task):
    """Hook called after contact saving task completion"""
    if task.success:
        result = task.result
        logger.info(
            f"vCard import completed successfully: "
            f"Task {task.id}, User {result.get('user_id')}, "
            f"Imported: {result.get('imported_count')}, "
            f"Failed: {result.get('failed_count')}"
        )
    else:
        logger.error(f"vCard import task {task.id} failed: {task.result}")


def enqueue_save_contacts_task(user_id: int, contacts: list[dict]) -> str:
    """Queue contact saving as background task"""
    task_id = async_task(
        "apps.contact.tasks.save_contacts_task",
        user_id,
        contacts,
        task_name=f"vcard_save_contacts_user_{user_id}",
        timeout=600,  # 10 minutes for large imports
        hook="apps.contact.tasks.save_contacts_hook",
    )

    logger.info(f"Queued contact saving task {task_id} for user {user_id}")
    return task_id


# Task enqueueing functions
def enqueue_cleanup_task() -> str:
    """Enqueue cleanup task immediately"""
    task_id = async_task(
        "apps.contact.tasks.cleanup_inactive_contacts",
        task_name="cleanup_inactive_contacts",
        timeout=300,  # 5 minutes timeout
        hook="apps.contact.tasks.cleanup_task_hook",
    )
    return f"Cleanup task enqueued with ID: {task_id}"


def enqueue_vcard_import_task(user_id: int, file_content: bytes) -> str:
    """Enqueue vCard import task for background processing

    Args:
        user_id: ID of the user who initiated the import
        file_content: Raw vCard file content

    Returns:
        str: Task ID for tracking
    """
    task_id = async_task(
        "apps.contact.tasks.process_vcard_import",
        user_id,
        file_content,
        task_name=f"vcard_import_user_{user_id}",
        timeout=600,  # 10 minutes timeout for large imports
        hook="apps.contact.tasks.vcard_import_hook",
    )

    return task_id


# Task hooks for logging and notifications
def cleanup_task_hook(task):
    """Hook called after cleanup task completion"""
    if task.success:
        logger.info(f"Cleanup task {task.id} completed successfully")
    else:
        logger.error(f"Cleanup task {task.id} failed: {task.result}")


def vcard_import_hook(task):
    """Hook called after vCard import task completion"""
    if task.success:
        logger.info(f"vCard import task {task.id} completed successfully")
        # Here you could send notification to user, update UI, etc.
    else:
        logger.error(f"vCard import task {task.id} failed: {task.result}")


# Scheduled tasks setup
def setup_periodic_tasks():
    """Setup periodic scheduled tasks"""

    # Schedule cleanup task to run daily at 2 AM
    schedule(
        "apps.contact.tasks.cleanup_inactive_contacts",
        name="daily_cleanup",
        schedule_type=Schedule.DAILY,
        minutes=0,
        hours=2,
        repeats=-1,  # Repeat indefinitely
    )

    logger.info("Periodic tasks scheduled successfully")


def send_email_notification(user_email: str, subject: str, message: str) -> bool:
    """Send email notification task

    Args:
        user_email: Recipient email
        subject: Email subject
        message: Email message

    Returns:
        bool: Success status
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        logger.info(f"Email sent successfully to {user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {e}")
        raise


def enqueue_email_notification(user_email: str, subject: str, message: str) -> str:
    """Enqueue email notification task"""
    task_id = async_task(
        "apps.contact.tasks.send_email_notification",
        user_email,
        subject,
        message,
        task_name=f"email_notification_{user_email}",
        timeout=60,
        hook="apps.contact.tasks.email_notification_hook",
    )

    return task_id


def email_notification_hook(task):
    """Hook for email notification task"""
    if task.success:
        logger.info(f"Email notification task {task.id} completed")
    else:
        logger.error(f"Email notification task {task.id} failed: {task.result}")
