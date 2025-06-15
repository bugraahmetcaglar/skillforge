import logging
import threading


class DatabaseLogHandler(logging.Handler):
    """PostgreSQL log handler using Django ORM"""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.local = threading.local()

    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record to PostgreSQL"""
        try:
            # Lazy import to avoid circular imports
            from apps.log.models import LogEntry

            # Get request context from middleware
            request_context = getattr(self.local, "request_context", {})

            # Create and save log entry
            LogEntry.create_from_log_record(record, request_context)

        except Exception as e:
            # Don't break the application if logging fails
            self.handleError(record)

    def set_request_context(self, **context):
        """Set request context (called by middleware)"""
        self.local.request_context = context

    def clear_request_context(self):
        """Clear request context"""
        if hasattr(self.local, "request_context"):
            delattr(self.local, "request_context")
