from typing import List
from currency_exchange.serialization.entity.currency import CurrencyEntity

from django.db.models import QuerySet
from currency_exchange.models import Currency as CurrencyORM


class CurrencyRepository:
    def get_currencies(self) -> List[CurrencyEntity]:
        currency_queryset: QuerySet[CurrencyORM] = self._get_queryset()

        return [self._orm_to_entity(orm=currency) for currency in currency_queryset]

    def check_currency_exists(self, currency: str) -> bool:
        return CurrencyORM.objects.filter(code=currency).exists()

    def _orm_to_entity(self, orm: CurrencyORM) -> CurrencyEntity:
        return CurrencyEntity.model_validate(orm)

    def _get_queryset(self) -> List[CurrencyORM]:
        return CurrencyORM.objects.all()
