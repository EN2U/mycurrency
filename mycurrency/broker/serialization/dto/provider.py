from datetime import date
from typing import List
from pydantic import BaseModel


class ProviderRetrieveDTO(BaseModel):
    code_list: List[str]
    current_date: date


class ProviderCreateDTO(BaseModel):
    name: str
    priority_order: int
