import abc
from datetime import date
from typing import Dict, List, Union


class CurrencyExchangeRateProvider(abc.ABC):
    def __init__(self, code: List[str], provider_url: str) -> None:
        self.code = code
        self.provider_url = provider_url

    @abc.abstractmethod
    def get_access_key(self) -> str:
        pass

    def create_url(self, current_date: date) -> str:
        access_key = self.get_access_key()
        code = ",".join(self.code)
        date_str = current_date.strftime(format="%Y-%m-%d")
        return f"{self.provider_url}{date_str}?access_key={access_key}&symbols={code}"

    @abc.abstractmethod
    def get_currency_exchange_rate_by_date(
        self, date: date
    ) -> Dict[str, Union[str, float]]:
        pass
