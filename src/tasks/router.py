import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.tasks.models import task
from src.references.models import ref_legal_docs, ref_section_card_debtor, ref_type_statement, ref_result_statement
from src.auth.models import user
from variables_for_backend import per_page_mov


# Получить по credit_id/добавить задачи
router_task = APIRouter(
    prefix="/v1/Tasks",
    tags=["Tasks"]
)


@router_task.get("/")
async def get_task(credit_id: int = None, section_card_debtor_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
        credit_item = credit_query.mappings().one()

        if section_card_debtor_id is not None and section_card_debtor_id != '':
            tasks_query = await session.execute(select(task).where(task.c.credit_id == credit_id).
                                                where(or_(task.c.section_card_debtor_id.in_((section_card_debtor_id, 1)),
                                                          task.c.section_card_debtor_id.is_(None))).order_by(desc(task.c.date_task)))
        else:
            tasks_query = await session.execute(select(task).where(task.c.credit_id == credit_id).order_by(desc(task.c.date_task)))

        tasks_set = tasks_query.mappings().all()

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item['debtor_id'])))
        debtor_item = debtor_query.mappings().one()

        if debtor_item.last_name_2 is not None:
            debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                         f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
        else:
            debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

        cession_query = await session.execute(select(cession.c.name).where(cession.c.id == int(credit_item.debtor_id)))
        cession_name = cession_query.scalar()

        result = []
        for item in tasks_set:

            section_task = ''
            section_task_id = None
            type_statement = ''
            type_statement_id = None
            result_statement = ''
            result_statement_id = None
            date_task = None
            date_statement = None
            date_answer = None

            name_task_query = await session.execute(select(ref_legal_docs.c.name).where(ref_legal_docs.c.id == int(item.name_id)))
            name_task = name_task_query.scalar()

            if item.section_card_debtor_id is not None:
                section_task_query = await session.execute(select(ref_section_card_debtor.c.name).where(ref_section_card_debtor.c.id == int(item.section_card_debtor_id)))
                section_task = section_task_query.scalar()
                section_task_id = item.section_card_debtor_id

            if item.type_statement_id is not None:
                type_stat_query = await session.execute(select(ref_type_statement.c.name).where(ref_type_statement.c.id == int(item.type_statement_id)))
                type_statement = type_stat_query.scalar()
                type_statement_id = item.type_statement_id

            if item.result_id is not None:
                result_stat_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == int(item.result_id)))
                result_statement = result_stat_query.scalar()
                result_statement_id = item['result_id']

            if item.date_task is not None:
                date_task = datetime.strptime(str(item.date_task), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_statement is not None:
                date_statement = datetime.strptime(str(item.date_statement), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_answer is not None:
                date_answer = datetime.strptime(str(item.date_answer), '%Y-%m-%d').strftime("%d.%m.%Y")

            user_query = await session.execute(select(user.c.first_name, user.c.last_name).where(user.c.id == int(item.user_id)))
            user_set = [item for item in user_query.mappings().all()]
            user_name = f'{user_set[0]["first_name"]} {user_set[0]["last_name"] or ""}'

            result.append({
                "id": item.id,
                "credit_id": item.credit_id,
                "number": credit_item.number,
                "debtorName": debtor_fio,
                "cession_name": cession_name,
                "name_task": name_task,
                "task_name_id": item.name_id,
                "type_statement": type_statement,
                "type_statement_id": type_statement_id,
                "section_card_debtor": section_task,
                "section_card_debtor_id": section_task_id,
                "date_task": date_task,
                "timeframe": item.timeframe,
                "user_name": user_name,
                "user_id": item.user_id,
                "date_statement": date_statement,
                "track_num": item.track_num,
                "date_answer": date_answer,
                "result": result_statement,
                "result_id": result_statement_id,
                "comment": item.comment,
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_task.post("/")
async def add_task(data: dict, session: AsyncSession = Depends(get_async_session)):

    task_id = data['id']

    if data['credit_id'] is None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }

    date_statement = None
    date_answer = None

    if data['date_task'] is not None:
        date_task = datetime.strptime(data['date_task'], '%Y-%m-%d').date()
    else:
        date_task = date.today()

    if data['date_statement'] is not None:
        date_statement = datetime.strptime(data['date_statement'], '%Y-%m-%d').date()
    if data['date_answer'] is not None:
        date_answer = datetime.strptime(data['date_answer'], '%Y-%m-%d').date()

    task_data = {
        "name_id": data["task_name_id"],
        "section_card_debtor_id": data["section_card_debtor_id"],
        "type_statement_id": data["type_statement_id"],
        "date_task": date_task,
        "timeframe": data["timeframe"],
        "user_id": data["user_id"],
        "date_statement": date_statement,
        "track_num": data["track_num"],
        "date_answer": date_answer,
        "result_id": data["result_id"],
        "credit_id": data["credit_id"],
        "comment": data['comment']
    }

    result = await func_save_task(task_id, task_data, session)

    return result


# Получить список всех задач
router_task_all = APIRouter(
    prefix="/v1/GetTasksAll",
    tags=["Tasks"]
)


@router_task_all.get("/")
async def get_task_all(page: int, user_id: int = None, name_task_id: int = None, session: AsyncSession = Depends(get_async_session)):

    per_page = per_page_mov

    try:
        if user_id and name_task_id == None:
            tasks_query = await session.execute(select(task).where(task.c.user_id == user_id).order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_query = await session.execute(select(func.count(distinct(task.c.id)).filter(task.c.user_id == user_id)))
        elif user_id == None and name_task_id:
            tasks_query = await session.execute(select(task).where(task.c.name_id == name_task_id).order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_query = await session.execute(select(func.count(distinct(task.c.id)).filter(task.c.name_id == name_task_id)))
        elif user_id and name_task_id:
            tasks_query = await session.execute(select(task).where(and_(task.c.user_id == user_id, task.c.name_id == name_task_id)).
                                                order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_query = await session.execute(select(func.count(distinct(task.c.id)).filter(and_(task.c.user_id == user_id, task.c.name_id == name_task_id))))
        else:
            tasks_query = await session.execute(select(task).order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_query = await session.execute(select(func.count(distinct(task.c.id))))

        total_item = total_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_tasks = []
        for item_task in tasks_query.mappings().all():

            date_task = None
            date_statement = None
            date_answer = None
            section_task = ''
            section_task_id = None
            type_statement = ''
            type_statement_id = None
            result_statement = ''
            result_statement_id = None

            credit_id = int(item_task.credit_id)
            credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
            credit_item = credit_query.mappings().one()

            debtor_id = int(credit_item.debtor_id)
            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()

            if debtor_item.last_name_2 is not None:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                             f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            cession_query = await session.execute(select(cession.c.name).where(cession.c.id == int(credit_item.cession_id)))
            cession_name = cession_query.scalar()

            name_task_query = await session.execute(select(ref_legal_docs.c.name).where(ref_legal_docs.c.id == int(item_task.name_id)))
            name_task = name_task_query.scalar()

            if item_task.section_card_debtor_id is not None:
                section_task_query = await session.execute(select(ref_section_card_debtor.c.name).where(ref_section_card_debtor.c.id == int(item_task.section_card_debtor_id)))
                section_task = section_task_query.scalar()
                section_task_id = item_task.section_card_debtor_id

            if item_task.type_statement_id is not None:
                type_stat_query = await session.execute(select(ref_type_statement.c.name).where(ref_type_statement.c.id == int(item_task.type_statement_id)))
                type_statement = type_stat_query.scalar()
                type_statement_id = item_task.type_statement_id

            if item_task.result_id is not None:
                result_stat_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == int(item_task.result_id)))
                result_statement = result_stat_query.scalar()
                result_statement_id = item_task.result_id

            if item_task.date_task is not None:
                date_task = datetime.strptime(str(item_task.date_task), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item_task.date_statement is not None:
                date_statement = datetime.strptime(str(item_task.date_statement), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item_task.date_answer is not None:
                date_answer = datetime.strptime(str(item_task.date_answer), '%Y-%m-%d').strftime("%d.%m.%Y")

            user_id = int(item_task.user_id)
            user_query = await session.execute(select(user.c.first_name, user.c.last_name).where(user.c.id == user_id))
            user_set = [item for item in user_query.mappings().all()]
            user_name = f'{user_set[0]["first_name"]} {user_set[0]["last_name"] or ""}'

            data_tasks.append({
                "id": item_task.id,
                "credit_id": item_task.credit_id,
                "credit_number": credit_item.number,
                "debtor_name": debtor_fio,
                "cession_name": cession_name,
                "name_task": name_task,
                "name_task_id": item_task.name_id,
                "type_statement": type_statement,
                "type_statement_id": type_statement_id,
                "section_card_debtor": section_task,
                "section_card_debtor_id": section_task_id,
                "date_task": date_task,
                "timeframe": item_task.timeframe,
                "user_name": user_name,
                "user_id": item_task.user_id,
                "date_statement": date_statement,
                "track_num": item_task.track_num,
                "date_answer": date_answer,
                "result": result_statement,
                "result_id": result_statement_id,
                "comment": item_task.comment,
            })

        result = {'data_tasks': data_tasks, 'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Удалить задачу
router_delete_task = APIRouter(
    prefix="/v1/DeleteTask",
    tags=["Tasks"]
)


@router_delete_task.delete("/")
async def delete_task(task_id: int, session: AsyncSession = Depends(get_async_session)):

    try:
        await session.execute(delete(task).where(task.c.id == task_id))
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Задача успешно удалена'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


async def func_save_task(task_id, data, session):

    try:
        if task_id:
            post_data = update(task).where(task.c.id == int(task_id)).values(data)
        else:
            post_data = insert(task).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Задача успешно сохранена'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }