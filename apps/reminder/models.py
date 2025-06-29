from django.db import models

from apps.finance.models import SubscriptionService
from apps.reminder.enums import ReminderStatusChoices, ExpenseCategoryChoices
from core.models import BaseModel
from core.enums import CurrencyChoices, PaymentMethodChoices


class BaseReminder(BaseModel):
    """
    Base model for reminders.
    This model can be extended to create specific reminder types.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(
        choices=ReminderStatusChoices.choices, default=ReminderStatusChoices.PENDING, max_length=35
    )

    reminder_date = models.DateTimeField(verbose_name="Reminder Date Time")
    scheduled_at = models.DateTimeField(auto_now=False, null=True, blank=True, verbose_name="Scheduled At")

    is_notified = models.BooleanField(default=False, verbose_name="Is Notified")
    is_recurring = models.BooleanField(default=False, verbose_name="Is Recurring")

    snoozed_until = models.DateTimeField(null=True, blank=True)
    snooze_count = models.PositiveIntegerField(default=0)

    def mark_as_completed(self):
        self.status = ReminderStatusChoices.COMPLETED
        self.save(update_fields=["status", "last_updated"])

    from datetime import datetime

    def mark_as_snoozed(self, snooze_until: datetime):
        if isinstance(snooze_until, str):
            try:
                snooze_until = datetime.fromisoformat(snooze_until)
            except ValueError:
                raise ValueError("Invalid datetime format for snooze_until. Expected ISO 8601 format.")
        self.snoozed_until = snooze_until
        self.snooze_count += 1
        self.status = ReminderStatusChoices.SNOOZED
        self.save(update_fields=["snoozed_until", "snooze_count", "status", "last_updated"])

    def mark_as_processing(self):
        self.status = ReminderStatusChoices.PROCESSING
        self.save(update_fields=["status", "last_updated"])

    def mark_as_failed(self):
        self.status = ReminderStatusChoices.FAILED
        self.save(update_fields=["status", "last_updated"])

    def mark_as_expired(self):
        self.status = ReminderStatusChoices.EXPIRED
        self.save(update_fields=["status", "last_updated"])

    class Meta:
        abstract = True


class FinanceReminder(BaseReminder):
    # Financial Core
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="TRY", choices=CurrencyChoices.choices)

    # Finance Type & Category
    finance_category = models.CharField(max_length=50, choices=ExpenseCategoryChoices.choices)

    # External Relations
    subscription = models.ForeignKey(
        SubscriptionService, null=True, blank=True, on_delete=models.PROTECT, related_name="finance_reminders"
    )

    # Payment Details
    payment_method = models.CharField(max_length=50, choices=PaymentMethodChoices.choices, blank=True)

    # Dates & Deadlines
    due_date = models.DateField(null=True, blank=True)
    grace_period_days = models.PositiveIntegerField(default=0)
    last_payment_date = models.DateField(null=True, blank=True, auto_now=False)
    next_payment_date = models.DateField(null=True, blank=True, auto_now=False)

    # Automation & Features
    autopay_enabled = models.BooleanField(default=False)
    send_sms_reminder = models.BooleanField(default=True)
    send_email_reminder = models.BooleanField(default=True)
    alert_days_before = models.PositiveIntegerField(default=3)

    # Penalty & Fees
    late_fee_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # User Association
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="finance_reminders", verbose_name="User"
    )

    class Meta:
        verbose_name = "Finance Reminder"
        verbose_name_plural = "Finance Reminders"
