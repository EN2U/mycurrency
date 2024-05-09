from typing import Dict, List
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from main.constants import FIXER_PROVIDER_NAME
from currency_exchange.serialization.serializer.currency_exchange_rate import (
    CurrencyExchangeConversionResponseSerializer,
    CurrencyExchangeRateResponseSerializer,
    CurrencyExchangeTimeseriesByCurrencyRequestSerializer,
    CurrencyExchangeTimeseriesRequestSerializer,
    CurrencyExhangeConversionRequestSerializer,
)
from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeConversionDTO,
    CurrencyExchangeConvertedDTO,
    CurrencyExchangeTimeseriesByCurrencyDTO,
    CurrencyExchangeTimeseriesDTO,
)
from currency_exchange.serialization.entity.currency_exchange_rate import (
    CurrencyExchangeRateEntity,
)
from currency_exchange.core.services.currency_exchange_rate import (
    CurrencyExchangeRateService,
)


class CurrencyExchangeViewSet(viewsets.ViewSet):

    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_rate_service = CurrencyExchangeRateService()

    def list(self, request: Request, *args, **kwargs) -> Response:
        print(":) list")
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        print(":) retrieve")
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        description="Return a timeseries given a range date",
        url_name="timeseries",
        url_path="timeseries/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})(?:/(?P<provider>\w+))?",
    )
    def timeseries(self, request: Request, *args, **kwargs) -> Response:
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        provider = kwargs.get("provider") or FIXER_PROVIDER_NAME

        data: Dict[str, str] = {
            "start_date": start_date,
            "end_date": end_date,
            "provider": provider,
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
        url_path="timeseries-by-currency/(?P<currency>\w+)/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})(?:/(?P<provider>\w+))?",
    )
    def timeseries_by_currency(self, request: Request, *args, **kwargs) -> Response:
        currency = kwargs.get("currency")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        provider = kwargs.get("provider") or FIXER_PROVIDER_NAME

        data: Dict[str, str] = {
            "start_date": start_date,
            "end_date": end_date,
            "provider": provider,
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
        url_path="conversion/(?P<source_currency>\w+)/(?P<amount>\d+(\.\d+)?)/(?P<target_currency>\w+)(?:/(?P<provider>\w+))?/latest",
    )
    def get_latest_currency_exchange(
        self, request: Request, *args, **kwargs
    ) -> Response:
        source_currency = kwargs.get("source_currency")
        target_currency = kwargs.get("target_currency")
        amount = kwargs.get("amount")
        provider = kwargs.get("provider") or FIXER_PROVIDER_NAME

        data: Dict[str, str] = {
            "source_currency": source_currency.upper(),
            "target_currency": target_currency.upper(),
            "provider": provider,
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
