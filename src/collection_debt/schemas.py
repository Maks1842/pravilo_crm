from pydantic import BaseModel
from datetime import date
from typing import Optional


class EDocCreate(BaseModel):
    id: Optional[int] = None
    number: str
    date: date
    case_number: str
    date_of_receipt_ed: date
    date_decision: date
    type_ed_id: Optional[int] = None
    status_ed_id: Optional[int] = None
    credit_id: int
    user_id: Optional[int] = None
    summa_debt_decision: int
    state_duty: int
    succession: date
    date_entry_force: date
    claimer_ed_id: Optional[int] = None
    tribunal_id: Optional[int] = None
    comment: str