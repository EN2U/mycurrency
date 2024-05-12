import abc
from datetime import date
from decimal import Decimal
from typing import Dict, List, Union


class CurrencyExchangeRateProvider(abc.ABC):
    def __init__(self, code_list: List[str], provider_url: str) -> None:
        self.code_list = code_list
        self.provider_url = provider_url

    @abc.abstractmethod
    def get_access_key(self) -> str:
        pass

    def create_url(self, current_date: date) -> str:
        access_key = self.get_access_key()
        code_str = ",".join(self.code_list)
        date_str = current_date.strftime(format="%Y-%m-%d")
        return (
            f"{self.provider_url}{date_str}?access_key={access_key}&symbols={code_str}"
        )

    @abc.abstractmethod
    def get_currency_exchange_rate_by_date(
        self, date: date
    ) -> Dict[str, Union[str, Dict[str, Decimal]]]:
        pass
