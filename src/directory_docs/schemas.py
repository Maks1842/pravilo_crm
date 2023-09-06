from pydantic import BaseModel
from typing import Optional


class DocsCessionCreate(BaseModel):
    id: Optional[int] = None
    name: str
    dir_cession_id: int
    path: str