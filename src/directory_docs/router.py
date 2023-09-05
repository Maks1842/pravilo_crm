from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.directory_docs.models import dir_cession


# Получить по credit_id директории Цессий
router_dir_cession = APIRouter(
    prefix="/v1/DirCession",
    tags=["DirectoryDocs"]
)


@router_dir_cession.get("/")
async def get_dir_cession(credit_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        credit_query = await session.execute(select(credit.c.cession_id).where(credit.c.id == credit_id))
        cession_id: int = credit_query.scalar()

        dir_cession_query = await session.execute(select(dir_cession).where(dir_cession.c.cession_id == cession_id))
        dir_cession_set = dir_cession_query.mappings().fetchone()

        result = {
                "dir_cession_id": dir_cession_set["id"],
                "dir_cession_name": dir_cession_set["name"],
                "dir_cession_path": dir_cession_set["path"]
            }
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }
