from pydantic import BaseModel
from datetime import date
from typing import Optional


class CessionSchema(BaseModel):
    id: int = None
    name: str
    number: str
    date: date = None
    summa: float = None
    cedent: str = None
    cessionari: str = None
    date_old_cession: str = None

    # class Config:
    #     orm_mode = True


class CessionCreate(BaseModel):
    id: Optional[int] = None
    name: str
    number: str
    date: date
    summa: float
    cedent: str
    cessionari: str
    date_old_cession: str