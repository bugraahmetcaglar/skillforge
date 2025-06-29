from django.db import models

from core.enums import BaseEnum


class SourceEnum(BaseEnum):
    VCARD = "vcard"


class ImportStatusChoices(models.TextChoices):
    """Status choices for import tasks"""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


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
