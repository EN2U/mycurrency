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
    CurrencyExchangeRateTWRRDTO,
    CurrencyExchangeTimeseriesByCurrenciesDTO,
    CurrencyExchangeRateCreateDTO,
    CurrencyExchangeTimeseriesByCurrencyDTO,
    CurrencyExchangeTimeseriesDTO,
)
from currency_exchange.serialization.entity.currency import CurrencyEntity
from currency_exchange.serialization.entity.currency_exchange_rate import (
    CurrencyExchangeRateEntity,
)
from broker.core.provider import ProviderService
from broker.provider.base.base_providers import (
    CurrencyExchangeRateProvider,
)
from broker.provider.base.providers_factory import (
    CurrencyExchangeRateProviderFactory,
)
from currency_exchange.core.services.currency import CurrencyService
from broker.serialization.dto.provider import ProviderRetrieveDTO


class CurrencyExchangeRateService:
    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_repository = CurrencyExchangeRateRepository()
        self._currency_service = CurrencyService()
        self._currency_exchange_rate_operations = CurrencyExchangeRateOperations()
        self._provider_service = ProviderService()

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
        )
        return currency_exchange_rate_entity_list

    def get_timeseries_by_currency(
        self, timeseries_by_currency_dto: CurrencyExchangeTimeseriesByCurrencyDTO
    ) -> List[CurrencyExchangeRateEntity]:
        self._validate_dates(
            start_date=timeseries_by_currency_dto.start_date,
            end_date=timeseries_by_currency_dto.end_date,
        )
        if not self.self._currency_service.check_currency_exists(
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

    def get_investment_rate_by_range(
        self,
        currency_exchange_investment_rate_dto: CurrencyExchangeTimeseriesByCurrenciesDTO,
    ) -> List[CurrencyExchangeRateTWRRDTO]:

        end_date = (datetime.now() - timedelta(days=1)).date()
        self._validate_dates(
            start_date=currency_exchange_investment_rate_dto.start_date,
            end_date=end_date,
        )
        if not self._currency_service.check_currency_exists(
            currency=currency_exchange_investment_rate_dto.source_currency
        ) or not self._currency_service.check_currency_exists(
            currency=currency_exchange_investment_rate_dto.target_currency
        ):
            raise ValueError("Invalid Currency code")

        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
            self._currency_exchange_repository.get_timeseries_by_source_target_currency(
                timeseries_by_currencies_dto=currency_exchange_investment_rate_dto
            )
        )

        self._check_time_series(
            currency_exchange_rate_entity_list=currency_exchange_rate_entity_list,
            start_date=currency_exchange_investment_rate_dto.start_date,
            end_date=end_date,
        )
        filtered_entities: List[CurrencyExchangeRateEntity] = (
            self._filter_entities_by_currencies(
                entities=currency_exchange_rate_entity_list,
                source_currency=currency_exchange_investment_rate_dto.source_currency,
                target_currency=currency_exchange_investment_rate_dto.target_currency,
            )
        )

        currency_exchange_rate_twrr_list: List[CurrencyExchangeRateTWRRDTO] = (
            self._get_twrr(
                amount=currency_exchange_investment_rate_dto.amount,
                entities=filtered_entities,
                start_date=currency_exchange_investment_rate_dto.start_date,
                end_date=end_date,
            )
        )

        return currency_exchange_rate_twrr_list

    def create_multiple(
        self, new_currency_exchange_rate_list_dto: CurrencyExchangeRateCreateDTO
    ) -> List[CurrencyExchangeRateEntity]:
        return self._currency_exchange_repository.create_multiple(
            new_currency_exchange_rate_list_dto=new_currency_exchange_rate_list_dto
        )

    def _get_twrr(
        self,
        amount: Decimal,
        entities: List[CurrencyExchangeRateEntity],
        start_date: date,
        end_date: date,
    ) -> List[CurrencyExchangeRateTWRRDTO]:
        twrr_daily_performance_list = []

        previous_value = amount
        cumulative_return = 0
        for entity in entities:
            if start_date <= entity.valuation_date <= end_date:
                current_value = (previous_value * entity.rate_value).quantize(
                    Decimal("1.000000")
                )
                daily_return = (
                    (current_value - previous_value) / previous_value
                ).quantize(Decimal("1.000000"))
                cumulative_return += daily_return
                twrr_daily_performance_list.append(
                    CurrencyExchangeRateTWRRDTO(
                        source_currency=entity.source_currency.code,
                        target_currency=entity.target_currency.code,
                        valuation_date=entity.valuation_date,
                        rate_value=entity.rate_value,
                        amount=current_value,
                        twrr=daily_return,
                        twrr_accumulated=cumulative_return,
                    )
                )
                previous_value = current_value

        return twrr_daily_performance_list

    def _validate_dates(self, start_date: date, end_date: date) -> None:
        if start_date > end_date:
            raise ValueError("Invalid date")

    def _check_time_series(
        self,
        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity],
        start_date: date,
        end_date: date,
    ) -> None:
        num_of_series_on_db = len(
            {rate.valuation_date for rate in currency_exchange_rate_entity_list}
        )
        num_of_series_required = (end_date - start_date + timedelta(days=1)).days
        if num_of_series_on_db != num_of_series_required:
            missing_dates = self._currency_exchange_rate_operations.find_missing_dates(
                current_date_list=[
                    rate.valuation_date.strftime("%Y-%m-%d")
                    for rate in currency_exchange_rate_entity_list
                ],
                start_date=start_date,
                end_date=end_date,
            )
            new_currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
                self._get_multiple_exchanges_rates_from_provider(dates=missing_dates)
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

    def _filter_entities_by_currencies(
        self,
        entities: List[CurrencyExchangeRateEntity],
        source_currency: str,
        target_currency: str,
    ) -> List[CurrencyExchangeRateEntity]:
        return [
            entity
            for entity in entities
            if entity.source_currency.code == source_currency
            and entity.target_currency.code == target_currency
        ]

    def _get_multiple_exchanges_rates_from_provider(
        self, dates: List[date]
    ) -> List[CurrencyExchangeRateEntity]:
        currency_entity_list: List[CurrencyEntity] = self._currency_service.retrieve()

        code_list: List[str] = [currency.code for currency in currency_entity_list]

        new_currency_exchange_rates: List[CurrencyExchangeRateCreateDTO] = []
        for current_date in dates:
            response = self._provider_service.retrieve(
                provider_retrieve_dto=ProviderRetrieveDTO(
                    current_date=current_date,
                    code_list=code_list,
                )
            )
            new_currency_exchange_rates_conversions: List[
                CurrencyExchangeRateCreateDTO
            ] = self._currency_exchange_rate_operations.calculate_exchange_rates_conversions(
                data=response
            )
            new_currency_exchange_rates: List[CurrencyExchangeRateCreateDTO] = (
                new_currency_exchange_rates + new_currency_exchange_rates_conversions
            )

        return self.create_multiple(
            new_currency_exchange_rate_list_dto=new_currency_exchange_rates
        )
