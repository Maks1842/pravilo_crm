from pydantic import BaseModel
from typing import Optional


class RefStatusCreditCreate(BaseModel):
    id: Optional[int] = None
    name: str