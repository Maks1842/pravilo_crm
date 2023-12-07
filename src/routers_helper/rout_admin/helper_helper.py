import os
import shutil
import re

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete, insert, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import executive_document, executive_productions
from src.directory_docs.models import dir_credit, docs_folder
from src.debts.models import cession, credit


# Роутер для запуска разных функций, вспомогательные вычисления
router_helper = APIRouter(
    prefix="/v1/Helper",
    tags=["Admin"]
)

@router_helper.get("/")
async def helper_helper(function, session: AsyncSession = Depends(get_async_session)):

    result = 'ERROR'
    if function == 'ed_delete':
        result = await ed_delete(session)
    elif function == 'add_docs_dossier':
        result = await add_docs_dossier(session)
    elif function == 'save_path_docs_folder':
        result = await save_path_docs_folder(session)
    elif function == 'filter_credit_status':
        result = await filter_credit_status(session)

    return result


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

    result = f'Успешно ed_delete'
    return result


# Метод копирования файлов в досье должников
async def add_docs_dossier(session):


    # !!!!! НЕОБХОДИМО ДОБАВИТЬ ЗАПИСТЬ ИНФОРМАЦИИ О ФАЙЛАХ В МОДЕЛЬ docs_folder


    path_out = '/home/maks/Загрузки/тест досье'
    path_in = '/media/maks/Новый том/Python/work/fast_api/pravilo_crm/Цессии_досье/Рубль_09_2023/Кредитные досье'

    folders_dossier_out = os.listdir(path_out)
    folders_dossier_in = os.listdir(path_in)

    count = 0
    count_docs_all = 0
    for f_out in folders_dossier_out:

        if re.findall(r'\d+-\d+', f_out):
            number_credit = re.search(r'\d+-\d+', f_out).group()
            path_folder = os.path.join(path_out, f_out)

            docs_dossier = os.listdir(path_folder)

            for f_in in folders_dossier_in:

                path_dir_cd = os.path.join(path_in, f'{f_in}/КД')

                number = re.search(r'\d+-\d+|\d{4}', f_in).group()

                if number in number_credit:

                    count_docs = copy_file(path_folder, docs_dossier, path_dir_cd)
                    count_docs_all += count_docs

                    count += 1
    result = f'Успешно скопировано {count_docs_all} документов, из {count} досье.'
    return result


def copy_file(path_folder, docs_dossier, path_dir_cd):

    count = 0
    for docs in docs_dossier:

        path_docs = os.path.join(path_folder, docs)
        shutil.copy2(path_docs, path_dir_cd)
        count += 1
    return count



# Метод записи Пути к документам досье
async def save_path_docs_folder(session):
    # path_out = '/media/maks/Новый том/Python/work/fast_api/pravilo_crm/Цессии_досье/Рубль_09_2023/Кредитные досье'

    # folders_dossier = os.listdir(path_out)

    query = await session.execute(select(dir_credit))

    count = 0
    for item in query.mappings().all():
        dir_credit_id = item.id
        path_dir_credit = item.path

        path_dir_folder = os.path.join(f'{path_dir_credit}/КД')

        docs_folder_list = os.listdir(path_dir_folder)

        for doc in docs_folder_list:
            doc_path = os.path.join(path_dir_folder, doc)

            data = {
                "name": doc,
                "name_folder": 'КД',
                "dir_credit_id": int(dir_credit_id),
                "path": doc_path
            }

            post_data = insert(docs_folder).values(data)

            await session.execute(post_data)
            await session.commit()

            count += 1

    result = f'Успешно записана инфа о {count} документах.'
    return result


# Тестовая функция сложного фильтра для статусов
async def filter_credit_status(session):

    list_cession = [9, 31, 32]
    list_status = [2, 11]
    credit_query = await session.execute(select(credit.c.id).where(and_(credit.c.cession_id.in_(list_cession), credit.c.status_cd_id.in_(list_status))))
    list_credit_id = credit_query.mappings().all()

    # for item in list_ed_id:
    #     ed_id: int = item.id
    #
    #     ep_query = await session.execute(select(executive_productions).where(executive_productions.c.executive_document_id == ed_id))
    #     ep_set = ep_query.fetchone()
    #
    #     if ep_set is None:
    #
    #         await session.execute(delete(executive_document).where(executive_document.c.id == ed_id))
    #         await session.commit()
    #         print(f'{ed_id=}')

    result = list_credit_id
    return result