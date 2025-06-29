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


class Environment(BaseEnum):
    """Environment choices for logging"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class CurrencyChoices(models.TextChoices):
    """Currency choices for financial models"""

    TRY = "TRY", "Turkish Lira"
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
    GBP = "GBP", "British Pound"
    JPY = "JPY", "Japanese Yen"
    CNY = "CNY", "Chinese Yuan"
    RUB = "RUB", "Russian Ruble"
    AUD = "AUD", "Australian Dollar"


class PaymentMethodChoices(models.TextChoices):
    # Credit & Debit Cards
    CREDIT_CARD = "credit_card", "Credit Card"
    DEBIT_CARD = "debit_card", "Debit Card"

    # Bank Transfer
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    WIRE_TRANSFER = "wire_transfer", "Wire Transfer"
    EFT = "eft", "EFT"

    # Digital Wallets - International
    PAYPAL = "paypal", "PayPal"
    APPLE_PAY = "apple_pay", "Apple Pay"
    GOOGLE_PAY = "google_pay", "Google Pay"
    SAMSUNG_PAY = "samsung_pay", "Samsung Pay"
    AMAZON_PAY = "amazon_pay", "Amazon Pay"

    # Turkish Digital Wallets & Banking
    PAYCELL = "paycell", "Paycell"
    TURKCELL_PAYCELL = "turkcell_paycell", "Turkcell Paycell"
    VODAFONE_CUZDAN = "vodafone_cuzdan", "Vodafone Cüzdan"

    # Buy Now Pay Later (BNPL)
    KLARNA = "klarna", "Klarna"
    MAXI = "maxi", "Maxi"
    HOPI = "hopi", "Hopi"

    # Cryptocurrency
    BITCOIN = "bitcoin", "Bitcoin"
    ETHEREUM = "ethereum", "Ethereum"
    USDT = "usdt", "USDT"
    BINANCE_PAY = "binance_pay", "Binance Pay"
    CRYPTO_OTHER = "crypto_other", "Other Cryptocurrency"

    # International Payment Systems
    STRIPE = "stripe", "Stripe"
    SQUARE = "square", "Square"

    # Alternative Methods
    CASH = "cash", "Cash"

    # Other
    OTHER = "other", "Other"
