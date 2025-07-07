from __future__ import annotations

from decimal import Decimal
from moneyed import Money as MoneyedMoney, Currency

from core.enums import CurrencyChoices


class Money:
    """Simple Money wrapper using py-moneyed"""

    def __init__(self, amount: Decimal | float | str, currency: str = CurrencyChoices.TRY):
        """Initialize Money object"""
        self.money = MoneyedMoney(amount=Decimal(str(amount)), currency=Currency(currency))

    @property
    def amount(self) -> Decimal:
        """Get the amount as Decimal with max 2 decimal places"""
        return self.money.amount.quantize(Decimal("0.01"))

    @property
    def currency_code(self) -> str:
        """Get currency code as string"""
        return str(self.money.currency)

    def __str__(self) -> str:
        """String representation"""
        return f"{self.amount} {self.currency_code}"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"Money({self.amount}, '{self.currency_code}')"

    def __eq__(self, other) -> bool:
        """Check equality"""
        if not isinstance(other, Money):
            return False
        return self.money == other.money

    def __add__(self, other: Money) -> Money:
        """Add two Money objects (same currency only)"""
        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot add {self.currency_code} to {other.currency_code}")

        result = self.money + other.money
        return Money(result.amount, result.currency)
