from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Union
from rest_framework import viewsets, status
from main.mixins import ResponseFormatViewMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from main.constants import FIXER_PROVIDER_NAME
from currency_exchange.serialization.serializer.currency_exchange_rate import (
    CurrencyExchangeRateResponseSerializer,
    CurrencyExchangeTimeseriesRequestSerializer,
)
from currency_exchange.serialization.dto.currency_exchange_rate import (
    CurrencyExchangeTimeSeriesDTO,
)
from currency_exchange.serialization.entity.currency_exchange_rate import (
    CurrencyExchangeRateEntity,
)
from currency_exchange.core.services.currency_exchange_rate import (
    CurrencyExchangeRateService,
)


class CurrencyExchangeViewSet(viewsets.ViewSet, ResponseFormatViewMixin):

    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_service = CurrencyExchangeRateService()

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

        data = {"start_date": start_date, "end_date": end_date, "provider": provider}
        timeseries_dates_serializer: CurrencyExchangeTimeseriesRequestSerializer = (
            CurrencyExchangeTimeseriesRequestSerializer(data=data)
        )

        timeseries_dates_serializer.is_valid(raise_exception=True)

        timeseries_dates_dto: CurrencyExchangeTimeSeriesDTO = (
            CurrencyExchangeTimeSeriesDTO(**timeseries_dates_serializer.validated_data)
        )

        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
            self._currency_exchange_service.get_timeseries(
                timeseries_dates_dto=timeseries_dates_dto
            )
        )

        response: List[CurrencyExchangeRateResponseSerializer] = (
            CurrencyExchangeRateResponseSerializer(
                currency_exchange_rate_entity_list, many=True
            )
        )

        return Response(data=response.data, status=status.HTTP_200_OK)
