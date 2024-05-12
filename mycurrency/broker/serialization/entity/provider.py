from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProviderEntity(BaseModel):
    name: str
    priority_order: int
    timeout: Optional[datetime]
    uuid: str

    class Config:
        from_attributes = True
