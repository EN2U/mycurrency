from datetime import date
from decimal import Decimal
import os
from typing import Dict, List, Union

import requests

from main.constants import FIXER_PROVIDER_NAME, FIXER_PROVIDER_URL
from broker.provider.base.base_providers import CurrencyExchangeRateProvider


class FixerProvider(CurrencyExchangeRateProvider):

    def __init__(self, code_list: List[str]) -> None:
        self.provider_name = FIXER_PROVIDER_NAME

        super().__init__(code_list=code_list, provider_url=FIXER_PROVIDER_URL)

    def get_access_key(self) -> str:
        return os.getenv("FIXER_API_KEY")

    def get_currency_exchange_rate_by_date(
        self, current_date: date
    ) -> Dict[str, Union[str, Dict[str, Decimal]]]:
        url = self.create_url(current_date=current_date)

        try:
            response = requests.request("GET", url)

            if 200 <= response.status_code < 500:
                return response.json(parse_float=Decimal)
            else:
                raise Exception(
                    f"HTTP {response.status_code} error while calling {response.url}"
                )
        except requests.RequestException:
            raise Exception(f"Connection failed while calling {response.url}")
