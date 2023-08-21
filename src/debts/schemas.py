from pydantic import BaseModel
from datetime import date
from typing import Optional


# class CessionSchema(BaseModel):
#     id: int = None
#     name: str
#     number: str
#     date: date = None
#     summa: float = None
#     cedent: str = None
#     cessionari: str = None
#     date_old_cession: str = None

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


class CreditCreate(BaseModel):
    id: Optional[int] = None
    creditor: str
    number: str
    date_start: date
    date_end: str
    summa_by_cession: float
    summa: float
    interest_rate: float
    overdue_od: float
    overdue_percent: float
    penalty: float
    percent_of_od: float
    gov_toll: float
    balance_debt: float
    debtor_id: int
    cession_id: int
    status_cd_id: int
    comment: str
    credits_old: str