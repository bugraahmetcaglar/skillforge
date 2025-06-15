from __future__ import annotations

from typing import List, Tuple
from enum import Enum
from django.db import models


class BaseEnum(Enum):
    """Base enum class with utility methods"""

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        """Generate Django/MongoEngine choices from enum"""
        return [(item.value, item.name.title()) for item in cls]

    @classmethod
    def values(cls) -> List[str]:
        """Get all enum values"""
        return [item.value for item in cls]

    @classmethod
    def names(cls) -> List[str]:
        """Get all enum names"""
        return [item.name for item in cls]

    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name for a value"""
        for item in cls:
            if item.value == value:
                return item.name.title()
        return value

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if value is valid for this enum"""
        return value in cls.values()

    def __str__(self) -> str:
        return self.value


class SourceTextChoices(models.TextChoices):
    GOOGLE = "google", "Google"
    OUTLOOK = "outlook", "Outlook"
    SIM = "sim", "SIM Card"
    ICLOUD = "icloud", "iCloud"
    CSV = "csv", "CSV File"
    MANUAL = "manual", "Manuel Entry"
    WHATSAPP = "whatsapp", "WhatsApp"
    TELEGRAM = "telegram", "Telegram"
    LINKEDIN = "linkedin", "LinkedIn"
    FACEBOOK = "facebook", "Facebook"
    INSTAGRAM = "instagram", "Instagram"
    TWITTER = "twitter", "Twitter"
    SAMSUNG = "samsung", "Samsung"
    VCARD = "vcard", "vCard"


class ImportStatus(models.TextChoices):
    """Status choices for import tasks"""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class Environment(BaseEnum):
    """Environment choices for logging"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
