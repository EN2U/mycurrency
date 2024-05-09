from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Union
from currency_exchange.data.repos.currency_exchange import (
    CurrencyExchangeRateRepository,
)
from currency_exchange.data.repos.currency import CurrencyRepository
from currency_exchange.utils import CurrencyExchangeRateOperations
from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeRateCreateDTO,
    CurrencyExchangeTimeSeriesDTO,
)
from currency_exchange.serialization.entity.currency import CurrencyEntity
from currency_exchange.serialization.entity.currency_exchange_rate import (
    CurrencyExchangeRateEntity,
)
from main.providers.base_providers import (
    CurrencyExchangeRateProvider,
)
from main.providers.providers_factory import (
    CurrencyExchangeRateProviderFactory,
)


class CurrencyExchangeRateService:
    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_repository = CurrencyExchangeRateRepository()
        self._currency_repository = CurrencyRepository()
        self._currency_exchange_operations = CurrencyExchangeRateOperations()

    def get_timeseries(
        self, timeseries_dates_dto: CurrencyExchangeTimeSeriesDTO
    ) -> None:

        if timeseries_dates_dto.start_date > timeseries_dates_dto.end_date:
            raise Exception("Invalid date")

        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
            self._currency_exchange_repository.get_timeseries(
                timeseries_dates_dto=timeseries_dates_dto
            )
            or []
        )

        num_of_series = (
            (timeseries_dates_dto.end_date - timeseries_dates_dto.start_date)
            + timedelta(days=1)
        ).days

        if len(currency_exchange_rate_entity_list) != num_of_series:
            missing_dates: List[date] = (
                self._currency_exchange_operations.find_missing_dates(
                    current_date_list=[
                        currency_exchange_rate_entity.valuation_date.strftime(
                            "%Y-%m-%d"
                        )
                        for currency_exchange_rate_entity in currency_exchange_rate_entity_list
                    ],
                    start_date=timeseries_dates_dto.start_date,
                    end_date=timeseries_dates_dto.end_date,
                )
            )
            new_currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
                self._get_multiple_exchanges_rates_from_provider(
                    dates=missing_dates, provider=timeseries_dates_dto.provider
                )
            )
            new_currency_exchange_rate_entity_list = (
                new_currency_exchange_rate_entity_list
                + new_currency_exchange_rate_entity_list
            )

        return currency_exchange_rate_entity_list

    def _get_multiple_exchanges_rates_from_provider(
        self, dates: List[date], provider: str
    ) -> List[CurrencyExchangeRateEntity]:
        currency_entity_list: List[CurrencyEntity] = (
            self._currency_repository.get_currencies()
        )
        currency_exchange_provider: Union[
            CurrencyExchangeRateProvider
        ] = CurrencyExchangeRateProviderFactory().get_exchange_provider(
            provider=provider,
            code=[currency.code for currency in currency_entity_list],
        )

        new_currency_exchange_rates: List[CurrencyExchangeRateCreateDTO] = []
        for current_date in dates:
            response: Dict[str, Union[str, Decimal]] = (
                currency_exchange_provider.get_currency_exchange_rate_by_date(
                    current_date=current_date
                )
            )
            new_currency_exchange_rates_conversions: List[
                CurrencyExchangeRateCreateDTO
            ] = self._currency_exchange_operations.calculate_exchange_rates_conversions(
                data=response
            )
            new_currency_exchange_rates: List[CurrencyExchangeRateCreateDTO] = (
                new_currency_exchange_rates + new_currency_exchange_rates_conversions
            )

        return (
            self._currency_exchange_repository.create_multiple_currency_exchange_rates(
                currency_exchange_rate_list_dto=new_currency_exchange_rates
            )
        )
