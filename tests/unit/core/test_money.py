import pytest
from decimal import Decimal
from moneyed import Money as Money

from core.money import Money


class TestMoney:
    """Unit tests for the Money class."""

    def test_money_creation_with_decimal(self):
        """Test creating Money with Decimal amount"""

        money = Money(Decimal("100.50"), "USD")

        assert money.amount == Decimal("100.50")
        assert money.currency_code == "USD"

    def test_money_creation_with_float(self):
        """Test creating Money with float amount"""

        money = Money(99.99, "EUR")
        assert money.amount == Decimal("99.99")
        assert money.currency_code == "EUR"

    def test_money_creation_with_string(self):
        """Test creating Money with string amount"""
        money = Money("75.25", "TRY")
        assert money.amount == Decimal("75.25")
        assert money.currency_code == "TRY"

    def test_money_creation_with_default_currency(self):
        """Test creating Money with default TRY currency"""
        money = Money("100.00")
        assert money.amount == Decimal("100.00")
        assert money.currency_code == "TRY"

    def test_amount_property(self):
        """Test amount property returns quantized Decimal"""
        money = Money("100.999", "USD")
        assert money.amount == Decimal("101.00")
        assert isinstance(money.amount, Decimal)

    def test_currency_code_property(self):
        """Test currency_code property returns string"""
        money = Money("100.00", "EUR")
        assert money.currency_code == "EUR"
        assert isinstance(money.currency_code, str)

    def test_str_representation(self):
        """Test string representation of Money object"""
        money = Money("100.50", "USD")
        assert str(money) == "100.50 USD"

    def test_repr_representation(self):
        """Test detailed string representation for debugging"""
        money = Money("100.50", "USD")
        assert repr(money) == "Money(amount=100.50, currency='USD')"

    def test_equality(self):
        """Test equality of Money objects with same currency and amount"""
        money1 = Money("100.00", "USD")
        money2 = Money("100.00", "USD")
        assert money1 == money2

    def test_not_equality(self):
        """Test inequality of Money objects with same currency but different amounts"""
        money1 = Money("100.00", "USD")
        money2 = Money("200.00", "USD")
        assert money1 != money2

    def test_equality_different_currency_same_amount(self):
        """Test inequality of Money objects with different currencies"""
        money1 = Money("100.00", "USD")
        money2 = Money("100.00", "EUR")
        assert money1 != money2

    def test_inequality_operator(self):
        """Test inequality operator"""
        money1 = Money("100.00", "USD")
        money2 = Money("200.00", "USD")
        assert money1 != money2

    def test_less_than(self):
        """Test less than comparison with same currency"""
        money1 = Money("100.00", "USD")
        money2 = Money("200.00", "USD")
        assert money1 < money2

    def test_less_than_or_equal(self):
        """Test less than or equal comparison with same currency"""
        money1 = Money("100.00", "USD")
        money2 = Money("100.00", "USD")
        money3 = Money("200.00", "USD")
        assert money1 <= money2
        assert money1 <= money3

    def test_greater_than(self):
        """Test greater than comparison with same currency"""
        money1 = Money("200.00", "USD")
        money2 = Money("100.00", "USD")
        assert money1 > money2

    def test_greater_than_or_equal(self):
        """Test greater than or equal comparison with same currency"""
        money1 = Money("200.00", "USD")
        money2 = Money("100.00", "USD")
        money3 = Money("200.00", "USD")
        assert money1 >= money2
        assert money1 >= money3

    def test_addition(self):
        """Test addition of Money objects with same currency"""
        money1 = Money("100.00", "USD")
        money2 = Money("50.00", "USD")
        result = money1 + money2

        assert isinstance(result, Money)
        assert result.amount == Decimal("150.00")
        assert str(result.currency_code) == "USD"

    def test_subtraction(self):
        """Test subtraction of Money objects with same currency"""
        money1 = Money("100.00", "USD")
        money2 = Money("30.00", "USD")
        result = money1 - money2

        assert isinstance(result, Money)
        assert result.amount == Decimal("70.00")
        assert str(result.currency_code) == "USD"

    def test_multiplication_by_decimal(self):
        """Test multiplication of Money by Decimal"""
        money = Money("100.00", "USD")
        result = money * Decimal("2.5")

        assert isinstance(result, Money)
        assert result.amount == Decimal("250.00")
        assert str(result.currency_code) == "USD"

    def test_multiplication_by_float(self):
        """Test multiplication of Money by float"""
        money = Money("100.00", "USD")
        result = money * 2.5

        assert isinstance(result, Money)
        assert result.amount == Decimal("250.00")
        assert str(result.currency_code) == "USD"

    def test_multiplication_by_int(self):
        """Test multiplication of Money by int"""
        money = Money("100.00", "USD")
        result = money * 3

        assert isinstance(result, Money)
        assert result.amount == Decimal("300.00")
        assert str(result.currency_code) == "USD"

    def test_division_by_decimal(self):
        """Test division of Money by Decimal"""
        money = Money("100.00", "USD")
        result = money / Decimal("2.0")

        assert isinstance(result, Money)
        assert result.amount == Decimal("50.00")
        assert str(result.currency_code) == "USD"

    def test_division_by_float(self):
        """Test division of Money by float"""
        money = Money("100.00", "USD")
        result = money / 4.0

        assert isinstance(result, Money)
        assert result.amount == Decimal("25.00")
        assert str(result.currency_code) == "USD"

    def test_division_by_int(self):
        """Test division of Money by int"""
        money = Money("100.00", "USD")
        result = money / 5

        assert isinstance(result, Money)
        assert result.amount == Decimal("20.00")
        assert str(result.currency_code) == "USD"

    def test_division_by_zero(self):
        """Test division of Money by zero raises ValueError"""
        money = Money("100.00", "USD")
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            money / 0

    def test_to_dict(self):
        """Test conversion of Money object to dictionary"""
        money = Money("100.50", "USD")
        result = money.to_dict()

        expected = {"amount": "100.50", "currency": "USD"}
        assert result == expected
        assert isinstance(result["amount"], str)
        assert isinstance(result["currency"], str)

    def test_money_creation_requires_currency_parameter(self):
        """Test that Money creation works with default TRY currency"""
        money = Money("100.00")
        assert money.amount == Decimal("100.00")
        assert money.currency_code == "TRY"

    def test_currency_precision_jpy_no_decimals(self):
        """Test JPY currency has 0 decimal places"""
        money = Money("100.567", "JPY")
        assert money.amount == Decimal("101")

    def test_currency_precision_bhd_three_decimals(self):
        """Test BHD currency has 3 decimal places"""
        money = Money("100.5678", "BHD")
        assert money.amount == Decimal("100.568")

    def test_automatic_rounding_in_init(self):
        """Test automatic rounding during initialization"""
        money = Money("100.999", "USD")
        assert money.amount == Decimal("101.00")  # ROUND_HALF_EVEN applies

    def test_string_amount_with_commas_cleaned(self):
        """Test creating Money with comma-separated string amount"""
        money = Money("1,234.56", "USD")
        assert money.amount == Decimal("1234.56")

    def test_arithmetic_operations_return_money_not_moneyed(self):
        """Test all arithmetic operations return Money objects, not Money"""
        money1 = Money("100.00", "USD")
        money2 = Money("50.00", "USD")

        result_add = money1 + money2
        assert isinstance(result_add, Money)
        assert result_add.amount == Decimal("150.00")
        assert result_add.currency_code == "USD"

        result_sub = money1 - money2
        assert isinstance(result_sub, Money)
        assert result_sub.amount == Decimal("50.00")
        assert result_sub.currency_code == "USD"

        result_mul = money1 * 2
        assert isinstance(result_mul, Money)
        assert result_mul.amount == Decimal("200.00")
        assert result_mul.currency_code == "USD"

        result_div = money1 / 2
        assert isinstance(result_div, Money)
        assert result_div.amount == Decimal("50.00")
        assert result_div.currency_code == "USD"

    def test_abs_method(self):
        """Test absolute value method"""
        negative_money = Money("-100.50", "USD")
        positive_money = negative_money.abs()

        assert isinstance(positive_money, Money)
        assert positive_money.amount == Decimal("100.50")
        assert positive_money.currency_code == "USD"

    def test_from_dict(self):
        """Test creating Money from dictionary"""
        data = {"amount": "100.50", "currency": "USD"}
        money = Money.from_dict(data)

        assert isinstance(money, Money)
        assert money.amount == Decimal("100.50")
        assert money.currency_code == "USD"
