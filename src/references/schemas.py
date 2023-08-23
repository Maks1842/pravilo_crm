from pydantic import BaseModel
from typing import Optional


class RefStatusCreditCreate(BaseModel):
    id: Optional[int] = None
    name: str


class RefTribunalCreate(BaseModel):
    id: Optional[int] = None
    name: str
    class_code: str
    oktmo: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gaspravosudie: Optional[bool] = False


class RefTypeDepartmentMovCreate(BaseModel):
    id: Optional[int] = None
    name: str


class RefRegionCreate(BaseModel):
    id: Optional[int] = None
    name: str
    index: int


class RefRospCreate(BaseModel):
    id: Optional[int] = None
    name: str
    type_department_id: int
    address: Optional[str] = None
    address_index: Optional[str] = None
    region_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    class_code: Optional[int] = None


class RefBankCreate(BaseModel):
    id: Optional[int] = None
    name: str
    type_department_id: int
    address: Optional[str] = None
    address_index: Optional[str] = None
    region_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bik: Optional[str] = None
    inn: Optional[str] = None
    corr_account: Optional[str] = None


class RefPfrCreate(BaseModel):
    id: Optional[int] = None
    name: str
    type_department_id: int
    address: Optional[str] = None
    address_index: Optional[str] = None
    region_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    class_code: Optional[int] = None
