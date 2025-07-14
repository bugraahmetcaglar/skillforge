import datetime
import logging
import requests

from django.conf import settings
from decimal import Decimal
from core.enums import CurrencyChoices


logger = logging.getLogger(__name__)


class ExchangeRateAPI:
    BASE_URL = "https://v6.exchangerate-api.com/v6/"
    EXCHANGE_RATE_API_KEY = settings.EXCHANGE_RATE_API_KEY
    DEFAULT_TIMEOUT = 30  # seconds

    def __init__(self):
        if not self.EXCHANGE_RATE_API_KEY:
            raise ValueError("Exchange Rate API key is not set in settings.")

        # Initialize the base URL for the Exchange Rate API
        self.base_url = self.BASE_URL + self.EXCHANGE_RATE_API_KEY

    def get_exchange_rate(
        self,
        base_currency: CurrencyChoices,
        target_currency: CurrencyChoices,
        target_date: datetime.date | None = None,
    ) -> Decimal:
        url = self.base_url

        if target_date:
            url += f"/history/{target_date.year}/{target_date.month}/{target_date.day}"
        else:
            url += f"/pair/{base_currency}/{target_currency}"

        response = requests.get(url, timeout=self.DEFAULT_TIMEOUT)

        if not response.ok:
            logger.error(
                f"Failed to fetch exchange rate for {base_currency} to {target_currency} on {target_date}. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )
            return Decimal("0")

        conversion_rate = response.json().get("conversion_rate", None)

        if not (conversion_rate and isinstance(conversion_rate, (Decimal, float, int))):
            logger.error(
                f"Conversion rate not found for {base_currency} to {target_currency} on {target_date}. "
                f"Response: {response.json()}"
            )
            return Decimal("0")

        return Decimal(conversion_rate).quantize(Decimal("0.01"))
