from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.references.models import ref_type_ed


# Получить/добавить тип ИД
router_ref_type_ed = APIRouter(
    prefix="/v1/RefTypeED",
    tags=["References"]
)


@router_ref_type_ed.get("/")
async def get_type_ed(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_type_ed))

        result = []
        for item in query.mappings().all():

            result.append({
                "type_ed": item.name,
                "value": {"type_ed_id": item.id},
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# # Удалить Статус ЕД
# router_delete_status_ed = APIRouter(
#     prefix="/v1/DeleteRefStatusED",
#     tags=["References"]
# )
#
#
# @router_delete_status_ed.delete("/")
# async def delete_status_ed(item_id: int, session: AsyncSession = Depends(get_async_session)):
#
#     try:
#         await session.execute(delete(ref_status_ed).where(ref_status_ed.c.id == item_id))
#         await session.commit()
#
#         return {
#             'status': 'success',
#             'data': None,
#             'details': 'Объект успешно удален'
#         }
#     except Exception as ex:
#         return {
#             "status": "error",
#             "data": None,
#             "details": ex
#         }