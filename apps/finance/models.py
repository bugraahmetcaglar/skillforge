from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db import models

from apps.finance.enums import BillingCycleChoices, SubscriptionStatusChoices
from apps.user.models import User
from core.enums import CurrencyChoices, PaymentMethodChoices
from core.models import BaseModel


class SubscriptionServiceCategory(BaseModel):
    """
    Model representing a category for subscription services.
    This can be extended to create specific categories.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Subscription Service Category"
        verbose_name_plural = "Subscription Service Categories"

    def __str__(self):
        return self.name


class SubscriptionService(BaseModel):
    """
    Model representing a subscription.
    This model can be extended to create specific subscription types.
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="Subscription Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    category = models.ForeignKey(
        SubscriptionServiceCategory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="subscription_services",
    )

    logo_url = models.URLField(null=True, blank=True, verbose_name="Logo URL")
    website_url = models.URLField(null=True, blank=True, verbose_name="Website URL")

    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Amount")
    currency = models.CharField(
        max_length=3, default=CurrencyChoices.TRY, choices=CurrencyChoices.choices, verbose_name="Currency"
    )
    payment_method = models.CharField(
        max_length=50, choices=PaymentMethodChoices.choices, null=True, blank=True, verbose_name="Payment Method"
    )

    free_trial_days = models.PositiveIntegerField(null=True, blank=True)
    free_trial_available = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False, verbose_name="Is Active")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Subscription Service"
        verbose_name_plural = "Subscription Services"


class UserSubscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_subscriptions")
    service = models.ForeignKey(SubscriptionService, on_delete=models.PROTECT, related_name="user_subscriptions")
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    # Plan & pricing
    plan_name = models.CharField(max_length=100, null=True, blank=True)  # "Premium", "Family", "Basic"
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.TRY)
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycleChoices.choices,
        default=BillingCycleChoices.MONTHLY,
        null=True,
        blank=True,
    )

    # Dates
    started_at = models.DateField()
    next_billing_date = models.DateField()
    trial_end_date = models.DateField(null=True, blank=True)
    cancelled_at = models.DateField(null=True, blank=True)

    # Status & settings
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatusChoices.choices,
        default=SubscriptionStatusChoices.ACTIVE,
    )
    auto_renewal = models.BooleanField(default=False)

    # Payment
    payment_method = models.CharField(max_length=50, choices=PaymentMethodChoices.choices)
    payment_account = models.CharField(max_length=100, blank=True)  # "Garanti *1234"

    # Notes
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "User Subscription"

    def refresh_next_billing_date(self):
        """Refreshes the next billing date based on the billing cycle.
        Raises ValueError if the next billing date is already in the future.
        """
        if date.today() < self.next_billing_date:
            raise ValueError("Next billing date is already in the future.")

        billing_cycle = {
            BillingCycleChoices.WEEKLY: timedelta(weeks=1),
            BillingCycleChoices.MONTHLY: relativedelta(months=1),
            BillingCycleChoices.QUARTERLY: relativedelta(months=3),
            BillingCycleChoices.SEMI_ANNUALLY: relativedelta(months=6),
            BillingCycleChoices.ANNUALLY: relativedelta(years=1),
        }
        self.next_billing_date = self.next_billing_date + billing_cycle.get(
            self.billing_cycle, relativedelta(months=1)
        )

        self.save(update_fields=["next_billing_date", "last_updated"])
