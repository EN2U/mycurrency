from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class CurrencyEntity(BaseModel):
    symbol: str
    code: str
    name: str

    class Config:
        from_attributes = True


class CurrencyExchangeRateEntity(BaseModel):
    id: int
    source_currency: CurrencyEntity
    target_currency: CurrencyEntity
    valuation_date: date
    rate_value: Decimal

    class Config:
        from_attributes = True
