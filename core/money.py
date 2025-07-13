from __future__ import annotations

from decimal import Decimal
from moneyed import Money as MoneyedMoney, Currency

from core.enums import CurrencyChoices


class Money:
    """A class to represent money with a specific currency."""

    money: MoneyedMoney

    def __new__(cls, amount: Decimal | float | str, currency: str = CurrencyChoices.TRY) -> Money:
        """Create a new Money instance with the specified amount and currency."""
        if not isinstance(amount, (Decimal, float, str)):
            raise TypeError("Amount must be a Decimal, float, or str")
        if isinstance(amount, str):
            try:
                amount = Decimal(amount)
            except ValueError:
                raise ValueError("Invalid string format for amount")
        if not isinstance(currency, str):
            raise TypeError("Currency must be a string")
        if currency not in CurrencyChoices:
            raise ValueError(f"Unsupported currency: {currency}")

        return super().__new__(cls)

    def __init__(self, amount: Decimal | float | str, currency: str = CurrencyChoices.TRY):
        """Initialize Money object"""
        if not hasattr(self, 'money'):
            self.money = MoneyedMoney(amount=Decimal(amount), currency=Currency(currency))
        if not isinstance(self.money, MoneyedMoney):
            raise TypeError("money must be an instance of MoneyedMoney")
        if self.money.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.money.currency.code != currency:
            raise ValueError(f"Currency mismatch: expected {currency}, got {self.money.currency.code}")

    @property
    def amount(self) -> Decimal:
        """Get the amount as Decimal with max 2 decimal places"""

        return self.money.amount.quantize(Decimal("0.01"))

    @property
    def currency_code(self) -> str:
        """Get currency code as string"""

        return str(self.money.currency)

    def __str__(self) -> str:
        """String representation of Money object"""

        return f"{self.amount} {self.currency_code}"

    def __repr__(self) -> str:
        """Detailed string representation for debugging"""

        return f"Money(amount={self.amount}, currency='{self.currency_code}')"

    def __eq__(self, other: object) -> bool:
        """Check equality of two Money objects (same currency only)"""
        if not isinstance(other, Money):
            raise TypeError("Comparison must be with another Money instance")
        return self.currency_code == other.currency_code and self.amount == other.amount

    def __ne__(self, other: Money) -> bool:
        """Check inequality of two Money objects (same currency only)"""
        if not isinstance(other, Money):
            raise TypeError("Comparison must be with another Money instance")
        return not self.__eq__(other)

    def __lt__(self, other: Money) -> bool:
        """Check if this Money is less than another (same currency only)"""
        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot compare {self.currency_code} with {other.currency_code}")
        return self.money < other.money

    def __le__(self, other: Money) -> bool:
        """Check if this Money is less than or equal to another (same currency only)"""
        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot compare {self.currency_code} with {other.currency_code}")
        return self.money <= other.money

    def __gt__(self, other: Money) -> bool:
        """Check if this Money is greater than another (same currency only)"""
        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot compare {self.currency_code} with {other.currency_code}")
        return self.money > other.money

    def __ge__(self, other: Money) -> bool:
        """Check if this Money is greater than or equal to another (same currency only)"""
        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot compare {self.currency_code} with {other.currency_code}")
        return self.money >= other.money

    def __add__(self, other: Money) -> MoneyedMoney:
        """Add two Money objects (same currency only)"""

        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot add {self.currency_code} to {other.currency_code}")
        return self.money + other.money

    def __sub__(self, other: Money) -> MoneyedMoney:
        """Subtract two Money objects (same currency only)"""

        if self.currency_code != other.currency_code:
            raise ValueError(f"Cannot subtract {self.currency_code} from {other.currency_code}")
        return self.money - other.money

    def __mul__(self, multiplier: Decimal | float | int) -> MoneyedMoney:
        """Multiply Money by a number"""

        if not isinstance(multiplier, (Decimal, float, int)):
            raise TypeError("Multiplier must be a number")
        return self.money * Decimal(multiplier)

    def __truediv__(self, divisor: Decimal | float | int) -> MoneyedMoney:
        """Divide Money by a number"""

        if not isinstance(divisor, (Decimal, float, int)):
            raise TypeError("Divisor must be a number")
        if divisor == 0:
            raise ValueError("Division by zero is not allowed")
        result = self.money.amount / Decimal(divisor)
        return MoneyedMoney(amount=result, currency=self.money.currency)

    def to_dict(self) -> dict:
        """Convert Money object to dictionary representation"""

        return {"amount": str(self.amount), "currency": self.currency_code}
