from django.db import models


class ExpenseCategoryChoices(models.TextChoices):
    PERSONAL = "personal", "Personal"
    BUSINESS = "business", "Business"
    INVESTMENT = "investment", "Investment"
    LOAN = "loan", "Loan"
    CREDIT_CARD = "credit_card", "Credit Card"
    MORTGAGE = "mortgage", "Mortgage"
    OTHER = "other", "Other"
    ENTERTAINMENT = "entertainment", "Entertainment"
    SUBSCRIPTION = "subscription", "Subscription"
    TRAVEL = "travel", "Travel"
    UTILITIES = "utilities", "Utilities"
    TRANSPORTATION = "transportation", "Transportation"
    FOOD = "food", "Food & Dining"
    SHOPPING = "shopping", "Shopping"
    HEALTH = "health", "Health & Medical"
    EDUCATION = "education", "Education"


class ReminderStatusChoices(models.TextChoices):
    """Status choices for import tasks"""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"
    SNOOZED = "snoozed", "Snoozed"
