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


class ContactSource(Enum):
    Google = SourceTextChoices.GOOGLE.value
    Outlook = SourceTextChoices.OUTLOOK.value
    Sim = SourceTextChoices.SIM.value
    ICloud = SourceTextChoices.ICLOUD.value
    Csv = SourceTextChoices.CSV.value
    Manual = SourceTextChoices.MANUAL.value
    WhatsApp = SourceTextChoices.WHATSAPP.value
    Telegram = SourceTextChoices.TELEGRAM.value
    LinkedIn = SourceTextChoices.LINKEDIN.value
    Facebook = SourceTextChoices.FACEBOOK.value
    Instagram = SourceTextChoices.INSTAGRAM.value
    Twitter = SourceTextChoices.TWITTER.value


class ImportStatus(models.TextChoices):
    """Status choices for import tasks"""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
