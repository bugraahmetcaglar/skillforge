from django.db import models

from apps.finance.enums import (
    BillStatusChoices,
    BillTypeChoices,
    BillingCycleChoices,
    SubscriptionServiceCategoryChoices,
    SubscriptionStatusChoices,
    UsageFrequencyChoices,
)
from apps.user.models import User
from core.enums import CurrencyChoices, PaymentMethodChoices
from core.models import BaseModel


class SubscriptionServiceCategory(BaseModel):
    """
    Model representing a category for subscription services.
    This can be extended to create specific categories.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, verbose_name="Description")

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

    name = models.CharField(max_length=255, verbose_name="Subscription Name")
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.ForeignKey(
        SubscriptionServiceCategory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="subscription_services",
    )

    logo_url = models.URLField(blank=True, verbose_name="Logo URL")
    website_url = models.URLField(blank=True, verbose_name="Website URL")

    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Amount")
    currency = models.CharField(
        max_length=3, default=CurrencyChoices.TRY, choices=CurrencyChoices.choices, verbose_name="Currency"
    )
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Payment Method")

    free_trial_days = models.PositiveIntegerField(null=True, blank=True)
    free_trial_available = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False, verbose_name="Is Active")

    class Meta:
        verbose_name = "Subscription Service"
        verbose_name_plural = "Subscription Services"
