from pydantic import BaseModel
from datetime import date


class CurrencyExchangeTimeSeriesDTO(BaseModel):
    start_date: date
    end_date: date
