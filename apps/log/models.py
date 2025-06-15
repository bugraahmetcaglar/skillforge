from __future__ import annotations

import logging

from django.db import models
from django.utils import timezone
from typing import Dict

from apps.log.enums import LogLevel
from core.enums import Environment
from core.models import BaseModel

logger = logging.getLogger(__name__)


class LogEntry(BaseModel):
    level = models.CharField(max_length=20, choices=LogLevel.choices(), db_index=True)
    message = models.TextField()
    logger_name = models.CharField(max_length=100, db_index=True)
    module = models.CharField(max_length=100, null=True, blank=True)
    function = models.CharField(max_length=100, null=True, blank=True)
    line_number = models.IntegerField(null=True, blank=True)

    extra_data = models.JSONField(default=dict, blank=True)

    user_id = models.CharField(max_length=26, null=True, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    request_path = models.CharField(max_length=500, null=True, blank=True)
    request_method = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["level", "created_at"]),
            models.Index(fields=["logger_name", "created_at"]),
            models.Index(fields=["user_id", "created_at"]),
        ]
        verbose_name = "Log Entry"
        verbose_name_plural = "Log Entries"

    def __str__(self) -> str:
        return f"{self.level} - {self.logger_name} - {self.message[:50]}"

    @classmethod
    def create_from_log_record(cls, record: logging.LogRecord, extra_context: Dict | None = None) -> LogEntry:
        """Create LogEntry from Python logging.LogRecord"""
        from datetime import datetime

        extra_context = extra_context or {}

        return cls.objects.create(
            timestamp=datetime.fromtimestamp(record.created, tz=timezone.get_current_timezone()),
            level=record.levelname,
            message=record.getMessage(),
            logger_name=record.name,
            module=getattr(record, "module", ""),
            function_name=getattr(record, "funcName", ""),
            line_number=getattr(record, "lineno", None),
            exception_info=record.exc_text if hasattr(record, "exc_text") else "",
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
