from datetime import timedelta
from typing import List
from django.shortcuts import render
from rest_framework import viewsets, status
from main.mixins import ResponseFormatViewMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializer import (
    CurrencyExchangeResponseSerializer,
    CurrencyExchangeTimeseriesRequestSerializer,
)
from .dtos import CurrencyExchangeTimeSeriesDTO
from .models import CurrencyExchangeRate as CurrencyExchangeRateORM
from django.db.models import QuerySet
from .entities import CurrencyExchangeRateEntity

# Create your views here.


class CurrencyExchangeViewSet(viewsets.ViewSet, ResponseFormatViewMixin):

    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_service = CurrencyExchangeService()

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
        url_path="timeseries/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})",
    )
    def timeseries(self, request: Request, *args, **kwargs) -> Response:
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        data = {"start_date": start_date, "end_date": end_date}
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

        response: List[CurrencyExchangeResponseSerializer] = (
            CurrencyExchangeResponseSerializer(
                currency_exchange_rate_entity_list, many=True
            )
        )

        return Response(data=response.data, status=status.HTTP_200_OK)


class CurrencyExchangeService:
    def __init__(self, *args, **kwargs) -> None:
        self._currency_exchange_repository = CurrencyExchangeRepository()

    def get_timeseries(
        self, timeseries_dates_dto: CurrencyExchangeTimeSeriesDTO
    ) -> None:
        currency_exchange_rate_entity_list: List[CurrencyExchangeRateEntity] = (
            self._currency_exchange_repository.get_timeseries(
                timeseries_dates_dto=timeseries_dates_dto
            )
        )

        num_of_series = (
            (timeseries_dates_dto.end_date - timeseries_dates_dto.start_date)
            + timedelta(days=1)
        ).days

        if not currency_exchange_rate_entity_list:
            print(":(")

        if not len(currency_exchange_rate_entity_list) != num_of_series:
            print(":(")

        return currency_exchange_rate_entity_list


class CurrencyExchangeRepository:
    def get_timeseries(
        self, timeseries_dates_dto: CurrencyExchangeTimeSeriesDTO
    ) -> List[CurrencyExchangeRateEntity]:
        currency_exchange_rate_orm_queryset: QuerySet[
            CurrencyExchangeRateORM
        ] = self._get_queryset().filter(
            valuation_date__gte=timeseries_dates_dto.start_date,
            valuation_date__lte=timeseries_dates_dto.end_date,
        )

        return [
            self._orm_to_entity(currency_exchange_rate_orm)
            for currency_exchange_rate_orm in currency_exchange_rate_orm_queryset
        ]

    def _orm_to_entity(
        self, currency_exchange_rate_orm: CurrencyExchangeRateORM
    ) -> CurrencyExchangeRateEntity:
        return CurrencyExchangeRateEntity.model_validate(currency_exchange_rate_orm)

    def _get_queryset(self) -> QuerySet[CurrencyExchangeRateORM]:
        return CurrencyExchangeRateORM.objects.select_related(
            "source_currency", "target_currency"
        ).all()
