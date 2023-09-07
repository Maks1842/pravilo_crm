from pydantic import BaseModel
from datetime import date
from typing import Optional


class IncomingMailCreate(BaseModel):
    id: Optional[int] = None
    sequence_num: int
    case_number: str
    credit_id: Optional[int] = None
    barcode: Optional[str] = None
    date: date
    addresser: Optional[str] = None
    name_doc_id: Optional[int] = None
    resolution_id: Optional[int] = None
    comment: Optional[str] = None