from typing import Dict, List
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from currency_exchange.serialization.serializer.currency_exchange_rate import (
    CurrencyExchangeConversionResponseSerializer,
    CurrencyExchangeRateTWRRResponseSerializer,
    CurrencyExchangeTWRRRequestSerializer,
    CurrencyExchangeRateResponseSerializer,
    CurrencyExchangeTimeseriesByCurrencyRequestSerializer,
    CurrencyExchangeTimeseriesRequestSerializer,
    CurrencyExhangeConversionRequestSerializer,
)
from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeConversionDTO,
    CurrencyExchangeConvertedDTO,
    CurrencyExchangeRateTWRRDTO,
    CurrencyExchangeTimeseriesByCurrenciesDTO,
    CurrencyExchangeTimeseriesByCurrencyDTO,
    CurrencyExchangeTimeseriesDTO,
)
from currency_exchange.serialization.entity.currency_exchange_rate import (
    CurrencyExchangeRateEntity,
)
from currency_exchange.core.services.currency_exchange_rate import (
    CurrencyExchangeRateService,
)


SOURCE_CURRENCY = "(?P<source_currency>\w+)"
AMOUNT = "(?P<amount>\d+(\.\d+)?)"
TARGET_CURRENCY = "(?P<target_currency>\w+)"
START_DATE = "(?P<start_date>\d{4}-\d{2}-\d{2})"
END_DATE = "(?P<end_date>\d{4}-\d{2}-\d{2})"
CURRENCY = "(?P<currency>\w+)"


class CurrencyExchangeViewSet(viewsets.ViewSet):

    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_rate_service = CurrencyExchangeRateService()

    @action(
        methods=["GET"],
        detail=False,
        description="Return a timeseries given a range date",
        url_name="timeseries",
        url_path="timeseries/" + START_DATE + "/" + END_DATE,
    )
    def timeseries(self, request: Request, *args, **kwargs) -> Response:
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        data: Dict[str, str] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        timeseries_dates_serializer: CurrencyExchangeTimeseriesRequestSerializer = (
            CurrencyExchangeTimeseriesRequestSerializer(data=data)
        )

        timeseries_dates_serializer.is_valid(raise_exception=True)

        timeseries_dates_dto: CurrencyExchangeTimeseriesDTO = (
            CurrencyExchangeTimeseriesDTO(**timeseries_dates_serializer.validated_data)
        )

        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
            self._currency_exchange_rate_service.get_timeseries(
                timeseries_dates_dto=timeseries_dates_dto
            )
        )

        response: List[CurrencyExchangeRateResponseSerializer] = (
            CurrencyExchangeRateResponseSerializer(
                currency_exchange_rate_entity_list, many=True
            )
        )

        return Response(data=response.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        description="Return a timeseries given by a range date from specific currency",
        url_name="timeseries-by-currency",
        url_path="timeseries-by-currency/"
        + CURRENCY
        + "/"
        + START_DATE
        + "/"
        + END_DATE,
    )
    def timeseries_by_currency(self, request: Request, *args, **kwargs) -> Response:
        currency = kwargs.get("currency")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        data: Dict[str, str] = {
            "start_date": start_date,
            "end_date": end_date,
            "currency": currency.upper(),
        }
        timeseries_serializer: CurrencyExchangeTimeseriesByCurrencyRequestSerializer = (
            CurrencyExchangeTimeseriesByCurrencyRequestSerializer(data=data)
        )

        timeseries_serializer.is_valid(raise_exception=True)

        timeseries_by_currency_dto: CurrencyExchangeTimeseriesByCurrencyDTO = (
            CurrencyExchangeTimeseriesByCurrencyDTO(
                **timeseries_serializer.validated_data
            )
        )

        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
            self._currency_exchange_rate_service.get_timeseries_by_currency(
                timeseries_by_currency_dto=timeseries_by_currency_dto
            )
        )

        response: List[CurrencyExchangeRateResponseSerializer] = (
            CurrencyExchangeRateResponseSerializer(
                currency_exchange_rate_entity_list, many=True
            )
        )

        return Response(data=response.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        description="Return the amount value converted from source to target currency",
        url_name="conversion",
        url_path="conversion/"
        + SOURCE_CURRENCY
        + "/"
        + AMOUNT
        + "/"
        + TARGET_CURRENCY
        + "/latest",
    )
    def get_latest_currency_exchange(
        self, request: Request, *args, **kwargs
    ) -> Response:
        source_currency = kwargs.get("source_currency")
        target_currency = kwargs.get("target_currency")
        amount = kwargs.get("amount")

        data: Dict[str, str] = {
            "source_currency": source_currency.upper(),
            "target_currency": target_currency.upper(),
            "amount": amount,
        }

        currency_exchange_conversion_serializer: (
            CurrencyExhangeConversionRequestSerializer
        ) = CurrencyExhangeConversionRequestSerializer(data=data)

        currency_exchange_conversion_serializer.is_valid(raise_exception=True)

        currency_exchange_conversion_dto: CurrencyExchangeConversionDTO = (
            CurrencyExchangeConversionDTO(
                **currency_exchange_conversion_serializer.validated_data
            )
        )

        currency_exchange_converted: CurrencyExchangeConvertedDTO = (
            self._currency_exchange_rate_service.get_currency_exchange_conversion(
                currency_exchange_conversion_dto=currency_exchange_conversion_dto
            )
        )

        response: CurrencyExchangeConversionResponseSerializer = (
            CurrencyExchangeConversionResponseSerializer(currency_exchange_converted)
        )

        return Response(response.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        description="Return the amount value converted from source to target currency",
        url_name="twrr",
        url_path=(
            "twrr/"
            + SOURCE_CURRENCY
            + "/"
            + AMOUNT
            + "/"
            + TARGET_CURRENCY
            + "/"
            + START_DATE
        ),
    )
    def get_twrr(self, request: Request, *args, **kwargs) -> Response:
        source_currency = kwargs.get("source_currency")
        target_currency = kwargs.get("target_currency")
        amount = kwargs.get("amount")
        start_date = kwargs.get("start_date")

        data: Dict[str, str] = {
            "source_currency": source_currency.upper(),
            "target_currency": target_currency.upper(),
            "amount": amount,
            "start_date": start_date,
        }

        currency_exchange_investment_rate_serializer: (
            CurrencyExchangeTWRRRequestSerializer
        ) = CurrencyExchangeTWRRRequestSerializer(data=data)

        currency_exchange_investment_rate_serializer.is_valid(raise_exception=True)

        currency_exchange_investment_rate_dto: (
            CurrencyExchangeTimeseriesByCurrenciesDTO
        ) = CurrencyExchangeTimeseriesByCurrenciesDTO(
            **currency_exchange_investment_rate_serializer.validated_data
        )

        currency_exchange_rate_twrr: List[CurrencyExchangeRateTWRRDTO] = (
            self._currency_exchange_rate_service.get_investment_rate_by_range(
                currency_exchange_investment_rate_dto=currency_exchange_investment_rate_dto
            )
        )

        response: CurrencyExchangeRateTWRRResponseSerializer = (
            CurrencyExchangeRateTWRRResponseSerializer(
                currency_exchange_rate_twrr, many=True
            )
        )

        return Response(response.data, status=status.HTTP_200_OK)
