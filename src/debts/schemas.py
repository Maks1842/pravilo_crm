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
    summa: int
    cedent: str
    cessionari: str
    date_old_cession: str


class CreditCreate(BaseModel):
    id: Optional[int] = None
    creditor: str
    number: str
    date_start: date
    date_end: str
    summa_by_cession: int
    summa: int
    interest_rate: float
    overdue_od: int
    overdue_percent: int
    penalty: int
    percent_of_od: int
    gov_toll: int
    balance_debt: int
    debtor_id: int
    cession_id: int
    status_cd_id: int
    comment: str
    credits_old: str