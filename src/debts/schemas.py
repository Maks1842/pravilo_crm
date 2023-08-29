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
    summa: Optional[int] = None
    cedent: str
    cessionari: str
    date_old_cession: str


class CreditCreate(BaseModel):
    id: Optional[int] = None
    creditor: str
    number: str
    date_start: date
    date_end: str
    summa_by_cession: Optional[int] = None
    summa: Optional[int] = None
    interest_rate: Optional[float] = None
    overdue_od: Optional[int] = None
    overdue_percent: Optional[int] = None
    penalty: Optional[int] = None
    percent_of_od: Optional[int] = None
    gov_toll: Optional[int] = None
    balance_debt: Optional[int] = None
    debtor_id: int
    cession_id: int
    status_cd_id: int
    comment: str
    credits_old: str