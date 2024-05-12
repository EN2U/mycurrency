from typing import List
from currency_exchange.data.repos.currency import CurrencyRepository
from currency_exchange.serialization.entity.currency import CurrencyEntity


class CurrencyService:
    def __init__(self, *args, **kwargs) -> None:
        self._currency_repository = CurrencyRepository()

    def retrieve(self) -> List[CurrencyEntity]:
        return self._currency_repository.get_currencies()

    def check_currency_exists(self, currency: str) -> bool:
        return self._currency_repository.check_currency_exists(currency=currency)
