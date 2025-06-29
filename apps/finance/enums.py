from django.db import models


class BillingCycleChoices(models.TextChoices):
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    SEMI_ANNUALLY = "semi_annually", "Semi-Annually"
    ANNUALLY = "annually", "Annually"


class SubscriptionStatusChoices(models.TextChoices):
    TRIAL = "trial", "Trial Period"
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"
    PENDING = "pending", "Pending Activation"


class BillTypeChoices(models.TextChoices):
    ELECTRICITY = "electricity", "Electricity"
    NATURAL_GAS = "natural_gas", "Natural Gas"
    WATER = "water", "Water"
    MOBILE_PHONE = "mobile_phone", "Mobile Phone"
    INTERNET = "internet", "Internet"
    LANDLINE = "landline", "Landline"
    CABLE_TV = "cable_tv", "Cable TV"
    RENT = "rent", "Rent"
    INSURANCE = "insurance", "Insurance"
    LOAN = "loan", "Loan Payment"
    CREDIT_CARD = "credit_card", "Credit Card"
    TAX = "tax", "Tax Payment"
    FINE = "fine", "Fine or Penalty"
    OTHER = "other", "Other"


class BillStatusChoices(models.TextChoices):
    UNSETTLED = "unsettled", "Unsettled"
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    TERMINATED = "terminated", "Terminated"
    SUSPENDED = "suspended", "Suspended"
