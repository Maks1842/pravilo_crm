from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.finance.models import ref_expenses_category, expenses
from src.debts.models import cession

import math
from datetime import datetime


# Получить/добавить Категории расходов
router_expenses_category = APIRouter(
    prefix="/v1/RefExpensesCategory",
    tags=["Finance"]
)


@router_expenses_category.get("/")
async def get_expenses_category(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_expenses_category))

        result = []
        for item in query.mappings().all():

            result.append({
                "expenses_category": item.name,
                "value": {
                    "expenses_category_id": item.id
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_expenses_category.post("/")
async def add_expenses_category(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    req_data = data_json['data_json']

    print(req_data)

    try:
        data = {
            "name": req_data['expenses_category'],
        }
        if req_data['value']["expenses_category_id"]:
            expenses_category_id: int = req_data['value']["expenses_category_id"]
            post_data = update(ref_expenses_category).where(ref_expenses_category.c.id == expenses_category_id).values(data)
        else:
            post_data = insert(ref_expenses_category).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Наименование категории успешно сохранено'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить расходы организации
router_expenses = APIRouter(
    prefix="/v1/Expenses",
    tags=["Finance"]
)


@router_expenses.get("/")
async def get_expenses(page: int, cession_id: int = None, expenses_category_id: int = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20

    if dates2 is None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    try:
        if cession_id and expenses_category_id is None and dates1 is None:
            query = await session.execute(select(expenses).where(expenses.c.cession_id == cession_id).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(expenses.c.cession_id == cession_id)))
        elif cession_id and expenses_category_id and dates1 is None:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.expenses_category_id == expenses_category_id)).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(expenses.c.cession_id == cession_id,
                                                                              expenses.c.expenses_category_id == expenses_category_id))))
        elif cession_id and expenses_category_id and dates1:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.date >= dates1, expenses.c.date <= dates2)).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(expenses.c.cession_id == cession_id,
                                                                              expenses.c.expenses_category_id == expenses_category_id,
                                                                              expenses.c.date >= dates1, expenses.c.date <= dates2))))
        elif cession_id and expenses_category_id is None and dates1:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.date >= dates1, expenses.c.date <= dates2)).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(expenses.c.cession_id == cession_id,
                                                                              expenses.c.date >= dates1, expenses.c.date <= dates2))))
        elif cession_id is None and expenses_category_id and dates1 is None:
            query = await session.execute(select(expenses).where(expenses.c.expenses_category_id == expenses_category_id).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(expenses.c.expenses_category_id == expenses_category_id)))
        elif cession_id is None and expenses_category_id and dates1:
            query = await session.execute(select(expenses).where(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.date >= dates1, expenses.c.date <= dates2)).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                              expenses.c.date >= dates1, expenses.c.date <= dates2))))
        elif cession_id is None and expenses_category_id is None and dates1:
            query = await session.execute(select(expenses).where(and_(expenses.c.date >= dates1, expenses.c.date <= dates2)).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(expenses.c.date >= dates1, expenses.c.date <= dates2))))
        else:
            query = await session.execute(select(expenses).order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(expenses.c.id)))

        total_item = total_item_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_expenses = []

        for item in query.mappings().all():

            summa_expenses = 0
            date_expenses = ''

            expenses_category_query = await session.execute(select(ref_expenses_category).where(ref_expenses_category.c.id == int(item.expenses_category_id)))
            expenses_category_set = expenses_category_query.mappings().fetchone()

            cession_query = await session.execute(select(cession).where(cession.c.id == int(item.cession_id)))
            cession_set = cession_query.mappings().fetchone()

            if item.summa:
                summa_expenses = item.summa / 100
            if item.date:
                date_expenses = datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y")

            data_expenses.append({
                "id": item.id,
                "date": date_expenses,
                "summa": summa_expenses,
                "expenses_category_id": expenses_category_set.id,
                "expenses_category": expenses_category_set.name,
                "payment_purpose": item.payment_purpose,
                "cession_id": cession_set.id,
                "cession_name": cession_set.name,

            })

        result = {'data_expenses': data_expenses,
                  'count_all': total_item,
                  'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_expenses.post("/")
async def add_expenses(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    req_data = data_json['data_json']

    date = None
    summa = None

    if req_data['date'] is not None:
        date = datetime.strptime(req_data['date'], '%Y-%m-%d').date()

    if req_data['summa'] is not None:
        summa = int(float(req_data['summa'])) * 100


    try:
        data = {
            "date": date,
            "summa": summa,
            "expenses_category_id": req_data['expenses_category_id'],
            "payment_purpose": req_data['payment_purpose'],
            "cession_id": req_data['cession_id'],
        }
        if req_data["id"]:
            expenses_id: int = req_data["id"]
            post_data = update(expenses).where(expenses.c.id == expenses_id).values(data)
        else:
            post_data = insert(expenses).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Расход успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }