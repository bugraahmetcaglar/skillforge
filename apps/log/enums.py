from core.enums import BaseEnum


class LogLevel(BaseEnum):
    """Log level choices"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    EXCEPTION = "EXCEPTION"
    CRITICAL = "CRITICAL"
