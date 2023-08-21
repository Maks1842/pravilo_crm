import re

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.tasks.models import task
from src.tasks.schemas import TaskCreate
from src.references.models import ref_task, ref_section_card_debtor, ref_type_statement, ref_result_statement
from src.auth.models import user


router_task = APIRouter(
    prefix="/v1/Tasks",
    tags=["Tasks"]
)


# Получить задачи по credit_id
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
            section_task_id = ''
            type_statement = ''
            type_statement_id = ''
            result_statement = ''
            result_statement_id = ''

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
                "creditNum": credit_item['number'],
                "debtorName": fio,
                "cessionName": cession_name,
                "nameTask": name_task,
                "nameTask_id": item_task['name_id'],
                "typeStatement": type_statement,
                "typeStatement_id": type_statement_id,
                "sectionTask": section_task,
                "sectionTask_id": section_task_id,
                "dateTask": item_task['date_task'],
                "timeFrame": item_task['timeframe'],
                "nameUser": user_name,
                "user_id": item_task['user_id'],
                "dateStatement": item_task['date_statement'],
                "trackNum": item_task['track_num'],
                "dateAnswer": item_task['date_answer'],
                "resultStatement": result_statement,
                "resultStatement_id": result_statement_id,
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


# Добавить/изменить задачу
@router_task.post("/")
async def add_cession(new_task: TaskCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_task.model_dump()

    if req_data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }

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

    try:
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