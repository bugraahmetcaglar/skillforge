from __future__ import annotations

from datetime import datetime, timedelta
import logging

from django.db import models
from django.db.models import Q
from django.utils import timezone
from typing import Dict

from apps.log.enums import LogLevel
from core.enums import Environment
from core.models import BaseModel

logger = logging.getLogger(__name__)


class LogEntry(BaseModel):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Core log fields
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    level = models.CharField(max_length=20, choices=LogLevel.choices(), db_index=True)
    message = models.TextField()
    logger_name = models.CharField(max_length=100, db_index=True)

    # Location info
    module = models.CharField(max_length=100, blank=True)
    function_name = models.CharField(max_length=100, blank=True)
    line_number = models.PositiveIntegerField(null=True, blank=True)

    # Request context
    user = models.ForeignKey(
        "user.User", null=True, blank=True, on_delete=models.DO_NOTHING, related_name="log_entries"
    )
    request_id = models.CharField(max_length=36, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True, db_index=True)

    # Performance metrics
    response_time_ms = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    status_code = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    # App context
    app_name = models.CharField(max_length=50, default="skillforge", db_index=True)
    environment = models.CharField(
        max_length=20, choices=Environment.choices(), default=Environment.DEVELOPMENT.value, db_index=True
    )

    # Additional data (JSON)
    extra_data = models.JSONField(default=dict, blank=True)
    exception_info = models.TextField(blank=True)

    class Meta:
        indexes = [
            # Compound indexes for common searches
            models.Index(fields=['level', '-timestamp']),
            models.Index(fields=['logger_name', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['app_name', 'level', '-timestamp']),
            
            # Performance indexes
            models.Index(fields=['request_path', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self) -> str:
        return f"{self.level} - {self.logger_name} - {self.message[:50]}"

    @classmethod
    def cleanup_old_logs(cls) -> bool:
        """Clean up old logs based on retention policy"""
        try:
            now = timezone.now()
            
            # Critical keywords that should never be deleted
            critical_keywords = [
                'SecurityError', 'AuthenticationFailed', 'DatabaseError', 
                'PaymentError', 'DataLoss', 'CRITICAL', 'SECURITY'
            ]
            
            # Build exclusion query for critical logs
            exclude_critical = Q()
            for keyword in critical_keywords:
                exclude_critical |= Q(message__icontains=keyword)
            
            cls.objects.annotate(
                should_delete=models.Case(
                    models.When(level='DEBUG', timestamp__lt=now - timedelta(days=7), then=True),
                    models.When(level='INFO', timestamp__lt=now - timedelta(days=30), then=True),
                    models.When(level='WARNING', timestamp__lt=now - timedelta(days=90), then=True),
                    models.When(level='ERROR', timestamp__lt=now - timedelta(days=365), then=True),
                    default=False,
                )
            ).filter(should_delete=True).exclude(exclude_critical).delete()
            return True

        except Exception as err:
            logger.exception(f"Error during log cleanup: {err}")
            return False

    @classmethod
    def create_from_log_record(cls, record: logging.LogRecord, extra_context: Dict | None = None):
        """Create LogEntry from Python logging.LogRecord"""
        extra_context = extra_context or {}

        exception_info = ""
        if hasattr(record, "exc_text") and record.exc_text:
            exception_info = record.exc_text
        elif hasattr(record, "exc_info") and record.exc_info:
            import traceback
            exception_info = "".join(traceback.format_exception(*record.exc_info))

        return cls.objects.create(
            timestamp=datetime.fromtimestamp(record.created, tz=timezone.get_current_timezone()),
            level=record.levelname,
            message=record.getMessage(),
            logger_name=record.name,
            module=getattr(record, "module", ""),
            function_name=getattr(record, "funcName", ""),
            line_number=getattr(record, "lineno", None),
            exception_info=exception_info,
            user_id=extra_context.get("user_id"),
            request_id=extra_context.get("request_id", ""),
            ip_address=extra_context.get("ip_address"),
            user_agent=extra_context.get("user_agent", ""),
            request_method=extra_context.get("request_method", ""),
            request_path=extra_context.get("request_path", ""),
            response_time_ms=extra_context.get("response_time_ms"),
            status_code=extra_context.get("status_code"),
            app_name=extra_context.get("app_name", "skillforge"),
            environment=extra_context.get("environment", Environment.DEVELOPMENT.value),
            extra_data={
                "process": record.process,
                "thread": record.thread,
                "pathname": record.pathname,
                **extra_context.get("extra_data", {}),
            },
        )
