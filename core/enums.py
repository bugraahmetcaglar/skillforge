from enum import Enum
from django.db import models


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


# TODO: Celery task implementation
class ImportStatus(models.TextChoices):
    """Status choices for import tasks"""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class SourceEnum(Enum):
    VCARD = "vcard"

    def __str__(self) -> str:
        return self.value
