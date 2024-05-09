from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Union

from currency_exchange.data.repos.currency_exchange import (
    CurrencyExchangeRateRepository,
)
from currency_exchange.data.repos.currency import CurrencyRepository
from currency_exchange.utils import CurrencyExchangeRateOperations
from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeConversionDTO,
    CurrencyExchangeConvertedDTO,
    CurrencyExchangeRateCreateDTO,
    CurrencyExchangeTimeseriesByCurrencyDTO,
    CurrencyExchangeTimeseriesDTO,
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
        self, timeseries_dates_dto: CurrencyExchangeTimeseriesDTO
    ) -> List[CurrencyExchangeRateEntity]:
        self._validate_dates(
            start_date=timeseries_dates_dto.start_date,
            end_date=timeseries_dates_dto.end_date,
        )
        currency_exchange_rate_entity_list = (
            self._currency_exchange_repository.get_timeseries(
                timeseries_dates_dto=timeseries_dates_dto
            )
            or []
        )
        self._check_time_series(
            currency_exchange_rate_entity_list=currency_exchange_rate_entity_list,
            start_date=timeseries_dates_dto.start_date,
            end_date=timeseries_dates_dto.end_date,
            provider=timeseries_dates_dto.provider,
        )
        return currency_exchange_rate_entity_list

    def get_timeseries_by_currency(
        self, timeseries_by_currency_dto: CurrencyExchangeTimeseriesByCurrencyDTO
    ) -> List[CurrencyExchangeRateEntity]:
        self._validate_dates(
            start_date=timeseries_by_currency_dto.start_date,
            end_date=timeseries_by_currency_dto.end_date,
        )
        if not self._currency_repository.check_currency_exists(
            currency=timeseries_by_currency_dto.currency
        ):
            raise ValueError("Invalid Currency code")

        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
            self._currency_exchange_repository.get_timeseries_by_currency(
                timeseries_by_currency_dto=timeseries_by_currency_dto
            )
            or []
        )
        self._check_time_series(
            currency_exchange_rate_entity_list=currency_exchange_rate_entity_list,
            start_date=timeseries_by_currency_dto.start_date,
            end_date=timeseries_by_currency_dto.end_date,
            provider=timeseries_by_currency_dto.provider,
        )
        filtered_entities: List[CurrencyExchangeRateEntity] = (
            self._filter_entities_by_currency(
                entities=currency_exchange_rate_entity_list,
                currency=timeseries_by_currency_dto.currency,
            )
        )
        return filtered_entities

    def get_currency_exchange_conversion(
        self, currency_exchange_conversion_dto: CurrencyExchangeConversionDTO
    ) -> CurrencyExchangeConvertedDTO:
        currency_exchange_rate_entity: CurrencyExchangeRateEntity = (
            self._currency_exchange_repository.get_by_source_target_currency(
                source_currency=currency_exchange_conversion_dto.source_currency,
                target_currency=currency_exchange_conversion_dto.target_currency,
            )
        )

        rate_value = currency_exchange_rate_entity.rate_value
        previous_date = (datetime.now() - timedelta(days=1)).date()
        if not currency_exchange_rate_entity.valuation_date == previous_date:
            new_currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
                self._get_multiple_exchanges_rates_from_provider(
                    dates=[previous_date],
                    provider=currency_exchange_conversion_dto.provider,
                )
            )

            matching_element = next(
                (
                    element
                    for element in new_currency_exchange_rate_entity_list
                    if element.source_currency.code
                    == currency_exchange_conversion_dto.source_currency
                    and element.target_currency.code
                    == currency_exchange_conversion_dto.target_currency
                ),
                None,
            )

            if not matching_element:
                raise Exception("Not found")

            rate_value = matching_element.rate_value

        return CurrencyExchangeConvertedDTO(
            source_currency=currency_exchange_conversion_dto.source_currency,
            target_currency=currency_exchange_conversion_dto.target_currency,
            amount=(currency_exchange_conversion_dto.amount * rate_value).quantize(
                Decimal("1.000000")
            ),
            rate_value=rate_value,
        )

    def _validate_dates(self, start_date: date, end_date: date) -> None:
        if start_date > end_date:
            raise ValueError("Invalid date")

    def _check_time_series(
        self,
        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity],
        start_date: date,
        end_date: date,
        provider: str,
    ) -> None:
        num_of_series_on_db = len(
            {rate.valuation_date for rate in currency_exchange_rate_entity_list}
        )
        num_of_series_required = (end_date - start_date + timedelta(days=1)).days
        if num_of_series_on_db != num_of_series_required:
            missing_dates = self._currency_exchange_operations.find_missing_dates(
                current_date_list=[
                    rate.valuation_date.strftime("%Y-%m-%d")
                    for rate in currency_exchange_rate_entity_list
                ],
                start_date=start_date,
                end_date=end_date,
            )
            new_currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
                self._get_multiple_exchanges_rates_from_provider(
                    dates=missing_dates, provider=provider
                )
            )
            currency_exchange_rate_entity_list.extend(
                new_currency_exchange_rate_entity_list
            )

    def _filter_entities_by_currency(
        self, entities: List[CurrencyExchangeRateEntity], currency: str
    ) -> List[CurrencyExchangeRateEntity]:
        return [
            entity for entity in entities if entity.source_currency.code == currency
        ]

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
