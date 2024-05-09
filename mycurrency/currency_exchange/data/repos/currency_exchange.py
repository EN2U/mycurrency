from typing import List
from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeRateCreateDTO,
    CurrencyExchangeTimeSeriesDTO,
)
from currency_exchange.serialization.entity.currency_exchange_rate import (
    CurrencyExchangeRateEntity,
)

from django.db.models import QuerySet

from currency_exchange.models import CurrencyExchangeRate as CurrencyExchangeRateORM


class CurrencyExchangeRateRepository:
    def get_timeseries(
        self, timeseries_dates_dto: CurrencyExchangeTimeSeriesDTO
    ) -> List[CurrencyExchangeRateEntity]:
        currency_exchange_rate_queryset: QuerySet[
            CurrencyExchangeRateORM
        ] = self._get_queryset().filter(
            valuation_date__gte=timeseries_dates_dto.start_date,
            valuation_date__lte=timeseries_dates_dto.end_date,
        )

        return [
            self._orm_to_entity(orm=currency_exchange_rate_orm)
            for currency_exchange_rate_orm in currency_exchange_rate_queryset
        ]

    def create_multiple_currency_exchange_rates(
        self, currency_exchange_rate_list_dto: List[CurrencyExchangeRateCreateDTO]
    ) -> List[CurrencyExchangeRateEntity]:

        return []
        currency_exchange_rate_queryset: QuerySet[CurrencyExchangeRateORM] = (
            CurrencyExchangeRateORM.objects.bulk_create(
                [
                    CurrencyExchangeRateORM(
                        source_currency_id=currency_exchange_rate_dto.source_currency,
                        target_currency_id=currency_exchange_rate_dto.target_currency,
                        valuation_date=currency_exchange_rate_dto.valuation_date,
                        rate_value=currency_exchange_rate_dto.rate_value,
                    )
                    for currency_exchange_rate_dto in currency_exchange_rate_list_dto
                ]
            )
        )

        return [
            self._orm_to_entity(orm=currency_exchange_rate_orm)
            for currency_exchange_rate_orm in currency_exchange_rate_queryset
        ]

    def _orm_to_entity(
        self, orm: CurrencyExchangeRateORM
    ) -> CurrencyExchangeRateEntity:
        return CurrencyExchangeRateEntity.model_validate(orm)

    def _get_queryset(self) -> QuerySet[CurrencyExchangeRateORM]:
        return CurrencyExchangeRateORM.objects.select_related(
            "source_currency", "target_currency"
        ).all()
