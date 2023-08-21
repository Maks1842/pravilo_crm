from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic.types import List

from src.database import get_async_session
from src.debts.models import *
from src.references.schemas import RefStatusCreditCreate


router_ref_status_credit = APIRouter(
    prefix="/v1/RefStatusCredit",
    tags=["References"]
)


# Добавить/изменить статус кредита
@router_ref_status_credit.post("/")
async def add_cession(new_status_credit: RefStatusCreditCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_status_credit.model_dump()

    try:

        if req_data["id"]:
            status_cd_id = int(req_data["id"])
            data = {
                "name": req_data["name"],
            }
            post_data = update(ref_status_credit).where(ref_status_credit.c.id == status_cd_id).values(data)
        else:
            data = {
                "name": req_data["name"],
                    }
            post_data = insert(ref_status_credit).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Статус КД успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }



