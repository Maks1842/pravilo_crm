import math
import re

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.tasks.models import task
from src.tasks.schemas import TaskCreate
from src.references.models import ref_task, ref_section_card_debtor, ref_type_statement, ref_result_statement
from src.auth.models import user


# Получить по credit_id/добавить задачи
router_task = APIRouter(
    prefix="/v1/Tasks",
    tags=["Tasks"]
)


@router_task.get("/")
async def get_cession(credit_id: int = None, section_card_debtor_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
        credit_item = dict(credit_query.one()._mapping)

        if section_card_debtor_id is not None and section_card_debtor_id != '':
            tasks_query = await session.execute(select(task).where(task.c.credit_id == credit_id).
                                                where(or_(task.c.section_card_debtor_id.in_((section_card_debtor_id, 1)),
                                                          task.c.section_card_debtor_id == None)).order_by(desc(task.c.date_task)))
        else:
            tasks_query = await session.execute(select(task).where(task.c.credit_id == credit_id).order_by(desc(task.c.date_task)))

        tasks_set = tasks_query.all()

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item['debtor_id'])))
        debtor_item = dict(debtor_query.one()._mapping)

        if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
            fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                  f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
        else:
            fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

        cession_query = await session.execute(select(cession.c.name).where(cession.c.id == int(credit_item['debtor_id'])))
        cession_name = cession_query.scalar()

        result = []
        for item in tasks_set:

            item_task = dict(item._mapping)

            section_task = ''
            section_task_id = None
            type_statement = ''
            type_statement_id = None
            result_statement = ''
            result_statement_id = None

            name_task_query = await session.execute(select(ref_task.c.name).where(ref_task.c.id == int(item_task['name_id'])))
            name_task = name_task_query.scalar()

            if item_task['section_card_debtor_id'] is not None and item_task['section_card_debtor_id'] != '':
                section_task_query = await session.execute(select(ref_section_card_debtor.c.name).where(ref_section_card_debtor.c.id == int(item_task['section_card_debtor_id'])))
                section_task = section_task_query.scalar()
                section_task_id = item_task['section_card_debtor_id']

            if item_task['type_statement_id'] is not None and item_task['type_statement_id'] != '':
                type_stat_query = await session.execute(select(ref_type_statement.c.name).where(ref_type_statement.c.id == int(item_task['type_statement_id'])))
                type_statement = type_stat_query.scalar()
                type_statement_id = item_task['type_statement_id']

            if item_task['result_id'] is not None and item_task['result_id'] != '':
                result_stat_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == int(item_task['result_id'])))
                result_statement = result_stat_query.scalar()
                result_statement_id = item_task['result_id']

            user_query = await session.execute(select(user.c.first_name, user.c.last_name).where(user.c.id == int(item_task['user_id'])))
            user_set = [dict(item._mapping) for item in user_query.all()]
            user_name = f'{user_set[0]["first_name"]} {user_set[0]["last_name"] or ""}'

            result.append({
                "id": item_task['id'],
                "credit_id": item_task['credit_id'],
                "number": credit_item['number'],
                "debtorName": fio,
                "cession_name": cession_name,
                "name_task": name_task,
                "nameTask_id": item_task['name_id'],
                "type_statement": type_statement,
                "type_statement_id": type_statement_id,
                "section_card_debtor": section_task,
                "section_card_debtor_id": section_task_id,
                "date_task": item_task['date_task'],
                "timeframe": item_task['timeframe'],
                "user_name": user_name,
                "user_id": item_task['user_id'],
                "date_statement": item_task['date_statement'],
                "track_num": item_task['track_num'],
                "date_answer": item_task['date_answer'],
                "result": result_statement,
                "result_id": result_statement_id,
                "comment": item_task['comment'],
            })
        return {
            'status': 'success',
            'data': result,
            'details': None
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_task.post("/")
async def add_cession(new_task: TaskCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_task.model_dump()

    if req_data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }

    try:
        data = {
            "name_id": req_data["name_id"],
            "section_card_debtor_id": req_data["section_card_debtor_id"],
            "type_statement_id": req_data["type_statement_id"],
            "date_task": req_data["date_task"],
            "timeframe": req_data["timeframe"],
            "user_id": req_data["user_id"],
            "date_statement": req_data["date_statement"],
            "track_num": req_data["track_num"],
            "date_answer": req_data["date_answer"],
            "result_id": req_data["result_id"],
            "credit_id": req_data["credit_id"],
            "comment": req_data['comment']
        }

        if req_data["id"]:
            task_id = int(req_data["id"])
            post_data = update(task).where(task.c.id == task_id).values(data)
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


# Получить список всех задач
router_task_all = APIRouter(
    prefix="/v1/GetTasksAll",
    tags=["Tasks"]
)


@router_task_all.get("/")
async def get_task_all(page: int, user_id: int = None, name_task_id: int = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20

    try:
        if user_id and name_task_id == None:
            tasks_query = await session.execute(select(task).where(task.c.user_id == user_id).order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(task.c.user_id == user_id)))
        elif user_id == None and name_task_id:
            tasks_query = await session.execute(select(task).where(task.c.name_id == name_task_id).order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(task.c.name_id == name_task_id)))
        elif user_id and name_task_id:
            tasks_query = await session.execute(select(task).where(and_(task.c.user_id == user_id, task.c.name_id == name_task_id)).
                                                order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(task.c.user_id == user_id, task.c.name_id == name_task_id))))
        else:
            tasks_query = await session.execute(select(task).order_by(desc(task.c.date_task)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(task.c.id)))

        total_item = total_item_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_tasks = []
        for item in tasks_query.all():
            item_task = dict(item._mapping)

            section_task = ''
            section_task_id = None
            type_statement = ''
            type_statement_id = None
            result_statement = ''
            result_statement_id = None

            credit_id = int(item_task['credit_id'])
            credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
            credit_item = dict(credit_query.one()._mapping)

            debtor_id = int(credit_item['debtor_id'])
            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = dict(debtor_query.one()._mapping)

            if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
                fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                      f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
            else:
                fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

            cession_query = await session.execute(select(cession.c.name).where(cession.c.id == int(credit_item['cession_id'])))
            cession_name = cession_query.scalar()

            name_task_query = await session.execute(select(ref_task.c.name).where(ref_task.c.id == int(item_task['name_id'])))
            name_task = name_task_query.scalar()

            if item_task['section_card_debtor_id'] is not None and item_task['section_card_debtor_id'] != '':
                section_task_query = await session.execute(select(ref_section_card_debtor.c.name).where(ref_section_card_debtor.c.id == int(item_task['section_card_debtor_id'])))
                section_task = section_task_query.scalar()
                section_task_id = item_task['section_card_debtor_id']

            if item_task['type_statement_id'] is not None and item_task['type_statement_id'] != '':
                type_stat_query = await session.execute(select(ref_type_statement.c.name).where(ref_type_statement.c.id == int(item_task['type_statement_id'])))
                type_statement = type_stat_query.scalar()
                type_statement_id = item_task['type_statement_id']

            if item_task['result_id'] is not None and item_task['result_id'] != '':
                result_stat_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == int(item_task['result_id'])))
                result_statement = result_stat_query.scalar()
                result_statement_id = item_task['result_id']

            user_id = int(item_task['user_id'])
            user_query = await session.execute(select(user.c.first_name, user.c.last_name).where(user.c.id == user_id))
            user_set = [dict(item._mapping) for item in user_query.all()]
            user_name = f'{user_set[0]["first_name"]} {user_set[0]["last_name"] or ""}'

            data_tasks.append({
                "id": item_task['id'],
                "credit_id": item_task['credit_id'],
                "credit_number": credit_item['number'],
                "debtor_name": fio,
                "cession_name": cession_name,
                "name_task": name_task,
                "name_task_id": item_task['name_id'],
                "type_statement": type_statement,
                "type_statement_id": type_statement_id,
                "section_card_debtor": section_task,
                "section_card_debtor_id": section_task_id,
                "date_task": item_task['date_task'],
                "timeframe": item_task['timeframe'],
                "user_name": user_name,
                "user_id": item_task['user_id'],
                "date_statement": item_task['date_statement'],
                "track_num": item_task['track_num'],
                "date_answer": item_task['date_answer'],
                "result": result_statement,
                "result_id": result_statement_id,
                "comment": item_task['comment'],
            })

        result = {'data_tasks': data_tasks, 'num_page_all': num_page_all}

        return {
            'status': 'success',
            'data': result,
            'details': None
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }