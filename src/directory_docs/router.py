import os

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit
from src.directory_docs.models import dir_cession, docs_cession, dir_credit, docs_folder, defolt_docs


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
                "dir_cession_id": dir_cession_set.id,
                "dir_cession_name": dir_cession_set.name,
                "dir_cession_path": dir_cession_set.path
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
async def get_file_cession(cession_id: int = None, credit_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            cession_id_query = await session.execute(select(credit.c.cession_id).where(credit.c.id == credit_id))
            cession_id: int = cession_id_query.scalar()

            dir_cession_query = await session.execute(select(dir_cession.c.id).where(dir_cession.c.cession_id == cession_id))
            dir_cession_id: int = dir_cession_query.scalar()
        else:
            dir_cession_query = await session.execute(select(dir_cession.c.id).where(dir_cession.c.cession_id == cession_id))
            dir_cession_id: int = dir_cession_query.scalar()

        docs_cession_query = await session.execute(select(docs_cession).where(docs_cession.c.dir_cession_id == dir_cession_id))

        result = []
        for item in docs_cession_query.mappings().all():

            result.append({
                "id": item.id,
                "docs_cession_name": item.name,
                "path": item.path
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

    dir_cession_id: int = dir_cession_set.id
    dir_cession_path = os.path.join(dir_cession_set.path, 'Договор цессии')

    path = os.path.join(dir_cession_path, file_name)

    with open(path, 'wb+') as f:
        for chunk in cession_file.file:
            f.write(chunk)

    try:
        docs_cession_qwery = await session.execute(select(docs_cession).where(docs_cession.c.name == file_name))
        docs_cession_set = docs_cession_qwery.mappings().fetchone()

        if docs_cession_set is None:

            data = {
                "name": file_name,
                "dir_cession_id": dir_cession_id,
                "path": path,
            }
            post_data = insert(docs_cession).values(data)

            await session.execute(post_data)
            await session.commit()
        else:
            return {
                'status': 'error',
                'data': None,
                'details': 'Невозможно сохранить. Файл с таким именем существует'
            }

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


# Скачать файл по цессии
router_download_file_cession = APIRouter(
    prefix="/v1/DownloadFileCession",
    tags=["DirectoryDocs"]
)


@router_download_file_cession.get("/")
async def download_file_cession(file_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        docs_cession_query = await session.execute(select(docs_cession).where(docs_cession.c.id == file_id))
        file_set = docs_cession_query.mappings().fetchone()

        path_file = file_set.path
        file_name = file_set.name

        # # отдаем сохраненный pdf в качестве ответа
        # file_pointer = open(path_file, "rb")
        # response = HttpResponse(file_pointer, content_type='application/pdf;')
        # response['Content-Disposition'] = f'attachment; filename={file_name}'


        return
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить по credit_id директории КД
router_dir_credit = APIRouter(
    prefix="/v1/DirCredit",
    tags=["DirectoryDocs"]
)


@router_dir_credit.get("/")
async def get_dir_credit(credit_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        dir_credit_query = await session.execute(select(dir_credit).where(dir_credit.c.credit_id == credit_id))
        dir_credit_set = dir_credit_query.mappings().fetchone()
        print(dir_credit_set)

        path_dir_cd = dir_credit_set.path
        print(path_dir_cd)

        folder_list = []
        for item in os.listdir(path_dir_cd):
            folder_list.append({'folder': item})

        result = {
            "dir_credit_id": dir_credit_set.id,
            "dir_credit_name": dir_credit_set.name,
            "dir_credit_path": path_dir_cd,
            "folder_list": folder_list
        }
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить по dir_id файлы по КД
router_docs_credit = APIRouter(
    prefix="/v1/CreditFile",
    tags=["DirectoryDocs"]
)


@router_docs_credit.get("/")
async def get_file_credit(credit_id: int = None, folder: str = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if folder:
            dir_credit_query = await session.execute(select(dir_credit.c.id).where(dir_credit.c.credit_id == credit_id))
            dir_credit_id: int = dir_credit_query.scalar()

            docs_folder_query = await session.execute(select(docs_folder).where(and_(docs_folder.c.dir_credit_id == dir_credit_id, docs_folder.c.name_folder == folder)))
        else:
            dir_credit_query = await session.execute(select(dir_credit.c.id).where(dir_credit.c.credit_id == credit_id))
            dir_credit_id: int = dir_credit_query.scalar()

            docs_folder_query = await session.execute(select(docs_folder).where(docs_folder.c.dir_credit_id == dir_credit_id))

        result = []
        for item in docs_folder_query.mappings().all():

            result.append({
                "id": item.id,
                "docs_credit_name": item.name,
                "path": item.path
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_docs_credit.post("/")
async def save_file_credit(credit_file: UploadFile, file_name: str, credit_id: int = None, folder: str = None, session: AsyncSession = Depends(get_async_session)):

    dir_credit_query = await session.execute(select(dir_credit).where(dir_credit.c.credit_id == credit_id))
    dir_credit_set = dir_credit_query.mappings().fetchone()

    dir_credit_id: int = dir_credit_set.id
    folder_path = os.path.join(dir_credit_set.path, folder)
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'wb+') as f:
        for chunk in credit_file.file:
            f.write(chunk)

    try:
        docs_folder_qwery = await session.execute(select(docs_folder).where(docs_folder.c.name == file_name))
        docs_folder_set = docs_folder_qwery.mappings().fetchone()

        if docs_folder_set is None:

            data = {
                "name": file_name,
                "name_folder": folder,
                "dir_credit_id": dir_credit_id,
                "path": file_path,
            }
            post_data = insert(docs_folder).values(data)

            await session.execute(post_data)
            await session.commit()
        else:
            return {
                'status': 'error',
                'data': None,
                'details': 'Невозможно сохранить. Файл с таким именем существует'
            }

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


# Получить/добавить Дефолтные наименования документов КД
router_defolt_docs = APIRouter(
    prefix="/v1/RefDefoltDocs",
    tags=["DirectoryDocs"]
)


@router_defolt_docs.get("/")
async def get_defolt_docs(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(defolt_docs))

        result = []
        for item in query.mappings().all():

            result.append({
                "defolt_docs": item.name,
                "value": {
                    "defolt_docs_id": item.id,
                    "folder_id": item.folder_id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }
