from fastapi import APIRouter, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic.types import List

from src.database import get_async_session
from src.debts.models import *
from src.debts.schemas import CessionCreate

router_cession_info = APIRouter(
    prefix="/v1/CessionInfo",
    tags=["Debts"]
)
