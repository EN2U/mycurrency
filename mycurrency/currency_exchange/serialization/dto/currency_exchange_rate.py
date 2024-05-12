from decimal import Decimal
from pydantic import BaseModel
from datetime import date


class CurrencyExchangeTimeseriesDTO(BaseModel):
    start_date: date
    end_date: date


class CurrencyExchangeRateCreateDTO(BaseModel):
    valuation_date: date
    rate_value: Decimal
    source_currency: str
    target_currency: str


class CurrencyExchangeTimeseriesByCurrencyDTO(CurrencyExchangeTimeseriesDTO):
    currency: str


class CurrencyExchangeConversionDTO(BaseModel):
    source_currency: str
    target_currency: str
    amount: Decimal


class CurrencyExchangeConvertedDTO(BaseModel):
    source_currency: str
    target_currency: str
    amount: Decimal
    rate_value: Decimal


class CurrencyExchangeTimeseriesByCurrenciesDTO(CurrencyExchangeConversionDTO):
    start_date: date


class CurrencyExchangeRateTWRRDTO(BaseModel):
    source_currency: str
    target_currency: str
    valuation_date: date
    rate_value: Decimal
    amount: Decimal
    twrr: Decimal
    twrr_accumulated: Decimal
