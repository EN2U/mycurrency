from datetime import date
from decimal import Decimal
from pydantic import BaseModel

from currency_exchange.serialization.entity.currency import CurrencyEntity


class CurrencyExchangeRateEntity(BaseModel):
    id: int
    source_currency: CurrencyEntity
    target_currency: CurrencyEntity
    valuation_date: date
    rate_value: Decimal

    class Config:
        from_attributes = True
