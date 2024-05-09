from pydantic import BaseModel


class CurrencyEntity(BaseModel):
    symbol: str
    code: str
    name: str

    class Config:
        from_attributes = True
