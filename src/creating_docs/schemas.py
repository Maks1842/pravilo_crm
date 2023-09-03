from pydantic import BaseModel
from typing import Optional


class DocsGeneratorTemplateCreate(BaseModel):
    id: Optional[int] = None
    name: str
    type_template_id: Optional[int] = None
    path_template_file: str