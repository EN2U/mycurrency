from decimal import Decimal
from pydantic import BaseModel
from datetime import date


class CurrencyExchangeTimeSeriesDTO(BaseModel):
    start_date: date
    end_date: date
    provider: str


class CurrencyExchangeRateCreateDTO(BaseModel):
    valuation_date: date
    rate_value: Decimal
    source_currency: str
    target_currency: str
