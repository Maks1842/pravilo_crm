from pydantic import BaseModel
from datetime import date


class CessionSchema(BaseModel):
    name: str
    number: str
    date: date = None
    summa: float = None
    cedent: str = None
    cessionari: str = None
    date_old_cession: str = None
    path: str = None

    class Config:
        orm_mode = True


class CessionCreate(BaseModel):
    id: int
    name: str
    number: str
    date: date
    summa: float
    cedent: str
    cessionari: str
    date_old_cession: str
    path: str