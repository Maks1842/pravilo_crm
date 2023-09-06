import os

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit
from src.directory_docs.models import dir_cession, docs_cession


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


# Получить по cession_id файлы Цессии
router_docs_cession = APIRouter(
    prefix="/v1/CessionFile",
    tags=["DirectoryDocs"]
)


@router_docs_cession.get("/")
async def get_file_cession(cession_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        dir_cession_query = await session.execute(select(dir_cession.c.id).where(dir_cession.c.cession_id == cession_id))
        dir_cession_id: int = dir_cession_query.scalar()

        docs_cession_query = await session.execute(select(docs_cession).where(docs_cession.c.dir_cession_id == dir_cession_id))

        result = []
        for item in docs_cession_query.mappings().all():

            result.append({
                "docs_cession_id": item["id"],
                "docs_cession_name": item["name"],
                "path": item["path"]
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_docs_cession.post("/")
async def save_file_cession(cession_file: UploadFile, file_name: str, cession_id: int = None, session: AsyncSession = Depends(get_async_session)):

    dir_cession_query = await session.execute(select(dir_cession).where(dir_cession.c.cession_id == cession_id))
    dir_cession_set = dir_cession_query.mappings().fetchone()

    dir_cession_id: int = dir_cession_set['id']
    dir_cession_path = os.path.join(dir_cession_set['path'], 'Договор цессии')

    path = os.path.join(dir_cession_path, file_name)

    with open(path, 'wb+') as f:
        for chunk in cession_file.file:
            f.write(chunk)

    try:
        data = {
            "name": file_name,
            "dir_cession_id": dir_cession_id,
            "path": path,
        }
        post_data = insert(docs_cession).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Файл успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при сохранении файла. {ex}"
        }
