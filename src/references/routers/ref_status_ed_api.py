from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.references.models import ref_status_ed


# Получить/добавить статус ИД
router_ref_status_ed = APIRouter(
    prefix="/v1/RefStatusED",
    tags=["References"]
)


@router_ref_status_ed.get("/")
async def get_status_ed(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_status_ed))

        result = []
        for item in query.mappings().all():

            result.append({
                "status_ed": item.name,
                "value": {"item_id": item.id,
                          "model": 'executive_document',
                          "field": 'status_ed_id'}
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_status_ed.post("/")
async def add_status_ed(req_data: dict, session: AsyncSession = Depends(get_async_session)):

    try:
        data = {
            "name": req_data["name"],
        }

        if req_data["id"]:
            status_ed_id = int(req_data["id"])
            post_data = update(ref_status_ed).where(ref_status_ed.c.id == status_ed_id).values(data)
        else:
            post_data = insert(ref_status_ed).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Статус ИД успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Удалить Статус ЕД
router_delete_status_ed = APIRouter(
    prefix="/v1/DeleteRefStatusED",
    tags=["References"]
)


@router_delete_status_ed.delete("/")
async def delete_status_ed(item_id: int, session: AsyncSession = Depends(get_async_session)):

    try:
        await session.execute(delete(ref_status_ed).where(ref_status_ed.c.id == item_id))
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