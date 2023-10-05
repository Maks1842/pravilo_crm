from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import executive_document, executive_productions


# Роутер для запуска разных функций, вспомогательные вычисления
router_helper = APIRouter(
    prefix="/v1/Helper",
    tags=["Admin"]
)

@router_helper.get("/")
async def helper_helper(session: AsyncSession = Depends(get_async_session)):

    ed_query = await session.execute(select(executive_document.c.id))
    list_ed_id = ed_query.mappings().all()

    for item in list_ed_id:
        ed_id: int = item.id

        ep_query = await session.execute(select(executive_productions).where(executive_productions.c.executive_document_id == ed_id))
        ep_set = ep_query.fetchone()

        if ep_set is None:

            await session.execute(delete(executive_document).where(executive_document.c.id == ed_id))
            await session.commit()
            print(f'{ed_id=}')