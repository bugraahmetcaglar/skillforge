from __future__ import annotations

import logging

from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any, Dict, Union
from moneyed import Money as MoneyedMoney, Currency

from core.enums import CurrencyChoices

Number = Union[Decimal, float, str, int]

logger = logging.getLogger(__name__)


class Money:
    """A class to represent money with a specific currency."""

    money: MoneyedMoney
    CURRENCY_PRECISION = {
        "JPY": 0,
        "KRW": 0,
        "VND": 0,
        "CLP": 0,  # No decimals
        "BHD": 3,
        "KWD": 3,
        "OMR": 3,  # 3 decimals
        # Most currencies default to 2 decimals
    }

    def __init__(self, amount: Union[str, int, float, Decimal], currency: str = CurrencyChoices.TRY):
        """Initialize Money object with automatic rounding.

        Args:
            amount: Monetary amount
            currency: 3-letter currency code (USD, EUR, TRY, etc.)
        """
        currency_code = currency.upper()

        # Convert to Decimal first
        if isinstance(amount, str):
            amount = amount.replace(",", "").strip()
        decimal_amount = Decimal(str(amount))

        # Get currency precision and round automatically
        precision = self.CURRENCY_PRECISION.get(currency_code, 2)
        quantizer = Decimal("0.1") ** precision
        rounded_amount = decimal_amount.quantize(quantizer, rounding=ROUND_HALF_EVEN)

        # Create internal moneyed object
        self.money = MoneyedMoney(rounded_amount, Currency(currency_code))

    @property
    def amount(self) -> Decimal:
        """Get the amount as Decimal"""

        return self.money.amount

    @property
    def currency_code(self) -> str:
        """Get currency code as string"""
        return str(self.money.currency.code)

    # ----------------------------------------------------
    # String representations
    # ----------------------------------------------------
    def __str__(self) -> str:
        """String representation of Money object"""

        return f"{self.amount} {self.currency_code}"

    def __repr__(self) -> str:
        """Detailed string representation for debugging"""

        return f"Money(amount={self.amount}, currency='{self.currency_code}')"

    # ----------------------------------------------------
    # Arithmetic operations
    # ----------------------------------------------------
    def __add__(self, other: Money) -> Money:

        """Add two money objects."""
        result = self.money + other.money
        return Money(result.amount, str(result.currency))

    def __sub__(self, other: Money) -> Money:
        """Subtract two money objects."""
        result = self.money - other.money
        return Money(result.amount, str(result.currency))

    def __mul__(self, multiplier: Union[int, float, Decimal]) -> Money:
        """Multiply money by number."""
        result_amount = self.amount * Decimal(str(multiplier))
        return Money(result_amount, self.currency_code)

    def __rmul__(self, multiplier: Union[int, float, Decimal]) -> Money:
        """Right multiply."""
        return self.__mul__(multiplier)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> Money:
        """Divide money by number."""
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        result_amount = self.amount / Decimal(str(divisor))
        return Money(result_amount, self.currency_code)

    # ----------------------------------------------------
    # Comparison operations
    # ----------------------------------------------------
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, Money):
            return False
        return self.money == other.money

    def __lt__(self, other: Money) -> bool:
        """Less than."""
        return self.money < other.money

    def __le__(self, other: Money) -> bool:
        """Less than or equal."""
        return self.money <= other.money

    def __gt__(self, other: Money) -> bool:
        """Greater than."""
        return self.money > other.money

    def __ge__(self, other: Money) -> bool:
        """Greater than or equal."""
        return self.money >= other.money

    # ----------------------------------------------------
    # Utility methods
    # ----------------------------------------------------
    def abs(self) -> Money:
        """Return absolute value."""
        return Money(abs(self.amount), self.currency_code)

    def copy(self) -> Money:
        """Create a copy of this Money object."""
        return Money(self.amount, self.currency_code)

    # ----------------------------------------------------
    # Serialization
    # ----------------------------------------------------
    def to_dict(self) -> dict:
        """Convert Money object to dictionary representation"""

        return {"amount": str(self.amount), "currency": self.currency_code}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Money:
        """Create Money from dictionary."""
        return cls(data['amount'], data['currency'])
