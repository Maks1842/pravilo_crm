from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.references.models import ref_status_credit


# Получить/добавить статус КД
router_ref_status_credit = APIRouter(
    prefix="/v1/RefStatusCredit",
    tags=["References"]
)


@router_ref_status_credit.get("/")
async def get_status_cd(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_status_credit))

        result = []
        for item in query.mappings().all():

            result.append({
                "status_cd": item.name,
                "value": {"item_id": item.id,
                          "model": 'credit',
                          "field": 'status_cd_id'}
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_status_credit.post("/")
async def add_status_cd(req_data: dict, session: AsyncSession = Depends(get_async_session)):

    try:
        data = {
            "name": req_data["name"],
        }

        if req_data["id"]:
            status_cd_id = int(req_data["id"])
            post_data = update(ref_status_credit).where(ref_status_credit.c.id == status_cd_id).values(data)
        else:
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


# Удалить Статус КД
router_delete_status_cd = APIRouter(
    prefix="/v1/DeleteRefStatusCredit",
    tags=["References"]
)


@router_delete_status_cd.delete("/")
async def delete_status_cd(item_id: int, session: AsyncSession = Depends(get_async_session)):

    try:
        await session.execute(delete(ref_status_credit).where(ref_status_credit.c.id == item_id))
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Объект успешно удален'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }