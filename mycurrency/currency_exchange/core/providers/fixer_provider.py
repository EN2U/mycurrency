from datetime import date
from decimal import Decimal
import os
from typing import Dict, List, Union

import requests

from main.constants import FIXER_PROVIDER_NAME, FIXER_PROVIDER_URL
from main.providers.base_providers import CurrencyExchangeRateProvider


class FixerProvider(CurrencyExchangeRateProvider):

    def __init__(self, code: List[str]) -> None:
        self.provider_name = FIXER_PROVIDER_NAME

        super().__init__(code=code, provider_url=FIXER_PROVIDER_URL)

    def get_access_key(self) -> str:
        return os.getenv("FIXER_API_KEY")

    def get_currency_exchange_rate_by_date(
        self, current_date: date
    ) -> Dict[str, Union[str, Decimal]]:
        url = self.create_url(current_date=current_date)
        return {
            "success": True,
            "timestamp": 1714780799,
            "historical": True,
            "base": "EUR",
            "date": str(current_date),
            "rates": {
                "CHF": Decimal("0.974775"),
                "EUR": Decimal("1"),
                "GBP": Decimal("0.858447"),
                "USD": Decimal("1.077179"),
            },
        }
        try:
            response = requests.request("GET", url)
        except Exception as e:
            raise e

        return response.json(parse_float=Decimal)
