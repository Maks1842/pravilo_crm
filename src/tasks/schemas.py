from pydantic import BaseModel
from datetime import date
from typing import Optional


class TaskCreate(BaseModel):
    id: Optional[int] = None
    name_id: Optional[int] = None
    section_card_debtor_id: Optional[int] = None
    type_statement_id: Optional[int] = None
    date_task: date
    timeframe: Optional[int] = None
    user_id: Optional[int] = None
    date_statement: date
    track_num: str
    date_answer: date
    result_id: Optional[int] = None
    credit_id: Optional[int] = None
    comment: str