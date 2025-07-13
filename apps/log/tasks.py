from __future__ import annotations

import logging
from datetime import datetime
from django_q.tasks import schedule
from django_q.models import Schedule

from apps.log.models import LogEntry

logger = logging.getLogger(__name__)


def cleanup_old_logs() -> dict:
    """Scheduled task to cleanup old logs based on retention policy"""

    try:
        # Run the cleanup
        cleanup_result = LogEntry.cleanup_old_logs()
        if not cleanup_result:
            logger.warning("Log cleanup did not delete any logs")
            return {"success": True, "message": "No logs deleted", "timestamp": datetime.now().isoformat()}

        logger.info("Log cleanup completed successfully")

        return {
            "success": True,
            "message": "Log cleanup completed successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as err:
        logger.error(f"Log cleanup failed: {err}", exc_info=True)
        return {"success": False, "error": str(err), "timestamp": datetime.now().isoformat()}


def warm_log_cache() -> dict:
    """Scheduled task to warm up log search caches"""

    try:
        from apps.log.services import LogSearchService

        logger.info("Starting log cache warming...")

        search_service = LogSearchService()
        warming_stats = search_service.warm_cache()

        logger.info(f"Cache warming completed: {warming_stats}")

        return {"success": True, "warming_stats": warming_stats, "timestamp": datetime.now().isoformat()}

    except Exception as err:
        logger.error(f"Cache warming failed: {err}", exc_info=True)
        return {"success": False, "error": str(err), "timestamp": datetime.now().isoformat()}


def setup_log_scheduled_tasks() -> dict:
    """Setup all log-related scheduled tasks"""

    try:
        # Clear existing schedules for logs
        Schedule.objects.filter(name__startswith="log_").delete()

        # 1. Daily cleanup at 3 AM
        schedule(
            "apps.log.tasks.cleanup_old_logs",
            name="log_daily_cleanup",
            schedule_type=Schedule.DAILY,
            next_run=datetime.now().replace(hour=3, minute=0, second=0, microsecond=0),
            repeats=-1,  # Infinite repeats
        )

        # 2. Cache warming every 2 hours
        schedule(
            "apps.log.tasks.warm_log_cache",
            name="log_cache_warming",
            schedule_type=Schedule.MINUTES,
            minutes=120,  # Every 2 hours
            repeats=-1,
        )

        # 3. Weekly deep cleanup (remove very old critical logs too)
        schedule(
            "apps.log.tasks.deep_cleanup_logs",
            name="log_weekly_deep_cleanup",
            schedule_type=Schedule.WEEKLY,
            next_run=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0),
            repeats=-1,
        )

        logger.info("Log scheduled tasks setup completed")

        return {"success": True, "message": "Log scheduled tasks setup completed"}

    except Exception as err:
        logger.error(f"Failed to setup log scheduled tasks: {err}")
        return {"success": False, "error": str(err)}


def deep_cleanup_logs() -> dict:
    """Weekly deep cleanup - remove very old logs including critical ones"""

    try:
        from datetime import timedelta

        logger.info("Starting deep log cleanup...")

        now = datetime.now()

        # Remove logs older than 2 years (even critical ones)
        two_years_old = now - timedelta(days=730)  # 2 years

        old_records = LogEntry.objects.filter(timestamp__lt=two_years_old)
        count = old_records.count()
        old_records.delete()

        logger.info("Deep cleanup completed successfully.")

        return {
            "success": True,
            "message": f"{count} logs older than 2 years will be deleted",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as err:
        logger.error(f"Deep cleanup failed: {err}", exc_info=True)
        return {"success": False, "error": str(err), "timestamp": datetime.now().isoformat()}


# Task hooks for monitoring
def cleanup_task_hook(task) -> None:
    """Hook called after cleanup task completion"""
    if task.success:
        logger.info(f"Cleanup task {task.id} completed successfully")
    else:
        logger.error(f"Cleanup task {task.id} failed: {task.result}")


def cache_warming_task_hook(task):
    """Hook called after cache warming task completion"""
    if task.success:
        logger.info(f"Cache warming task {task.id} completed successfully")
    else:
        logger.error(f"Cache warming task {task.id} failed: {task.result}")
