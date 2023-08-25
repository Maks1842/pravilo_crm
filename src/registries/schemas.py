from pydantic import BaseModel
from typing import Optional


class RegistryHeadersCreate(BaseModel):
    id: Optional[int] = None
    model: str
    name_field: str
    headers: str
    headers_key: str
    width_field: int