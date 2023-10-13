import os
import shutil
import re

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
async def helper_helper(function, session: AsyncSession = Depends(get_async_session)):

    if function == 'ed_delete':
        await ed_delete(session)
    elif function == 'add_docs_dossier':
        await add_docs_dossier(session)


# Метод удаления записей из Таблицы executive_document
async def ed_delete(session):
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


# Метод копирования файлов в досье должников
async def add_docs_dossier(session):
    path_out = '/home/maks/Документы/ИКЦ Правило'
    path_in = '/media/maks/Новый том/Python/work/fast_api/pravilo_crm/Цессии_досье/Рубль_09_2023/Кредитные досье'

    folders_dossier_out = os.listdir(path_out)
    folders_dossier_in = os.listdir(path_in)

    for f_out in folders_dossier_out:

        if re.findall(r'\d{6}', f_out):
            number_credit = re.search(r'\d{6}', f_out).group()
            path_folder = os.path.join(path_out, f_out)

            docs_dossier = os.listdir(path_folder)

            for f_in in folders_dossier_in:

                path_dir_cd = os.path.join(path_in, f'{f_in}/КД')

                number = re.search(r'\d+', f_in).group()

                if number in number_credit:
                    print(f'{path_folder=}')
                    print(f'{path_dir_cd=}')

                    # shutil.copy2(path_folder, path_dir_cd)
                    #
                    # print(f'{f_in=}')