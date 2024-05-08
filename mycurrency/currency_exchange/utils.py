from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Union
from .models import Currency, CurrencyExchangeRate
from django.db.models import QuerySet
from main.settings import DEFAULT_CURRENCY_PROVIDER_URL
import os
import requests

MAX_NUMBER_OF_CURRENCY_EXCHANGES_RATES = 2


def initialize_currency_exchange_db(*args, **kwargs):
    currency_list: QuerySet = Currency.objects.all().values_list("code", flat=True)

    latest_exchange_rate = None
    currency_exchange_provider = CurrencyExchangeProvider(symbols=currency_list)

    try:
        latest_exchange_rate = CurrencyExchangeRate.objects.latest("valuation_date")
    except CurrencyExchangeRate.DoesNotExist:
        latest_exchange_rate: datetime = datetime.now() - timedelta(
            days=MAX_NUMBER_OF_CURRENCY_EXCHANGES_RATES + 1
        )
        new_currency_exchange_list = {
            "success": True,
            "timestamp": 1714780799,
            "historical": True,
            "base": "EUR",
            "date": "2024-05-03",
            "rates": {
                "CHFCurrencyExchangeInitializer": Decimal("0.974775"),
                "EUR": Decimal("1"),
                "GBP": Decimal("0.858447"),
                "USD": Decimal("1.077179"),
            },
        }
        return
        # for x in range(MAX_NUMBER_OF_CURRENCY_EXCHANGES_RATES):
        #     new_currency_exchange_list.append(
        #         currency_exchange_provider.get_currencies_by_date(
        #             date=latest_exchange_rate
        #         )
        #     )
        # create object

    if not latest_exchange_rate < datetime.now() - timedelta(days=1):
        print("data is not correctly perserved")

        new_currency_exchange_list = []
        while latest_exchange_rate < datetime.now():
            new_currency_exchange_list.append(
                currency_exchange_provider.get_currencies_by_date(
                    date=latest_exchange_rate
                )
            )
            latest_exchange_rate = latest_exchange_rate + timedelta(days=1)

        # create object

    # execute some logic


class CurrencyExchangeProvider:

    def __init__(
        self, symbols: List[str], provider_url: str = DEFAULT_CURRENCY_PROVIDER_URL
    ) -> None:
        self.provider_url = provider_url
        self.symbols = symbols

    def get_access_key(self) -> str:
        return os.getenv("FIXER_API_KEY")

    def create_url(self, date: datetime) -> str:
        return f"{self.provider_url}{str(date.date())}?access_key={self.get_access_key()}&symbols={','.join(self.symbols)}"

    def get_currencies_by_date(self, date: datetime) -> Dict[str, Union[str, float]]:
        url = self.create_url(date=date)

        return

        try:
            response = requests.request("GET", url)
        except Exception as e:
            raise e

        return response.json(parse_float=Decimal)
