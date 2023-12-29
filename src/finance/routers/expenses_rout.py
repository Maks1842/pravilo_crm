from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, insert, func, distinct, update, and_, desc, true, false
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.finance.models import ref_expenses_category, expenses
from src.debts.models import cession

import math
from datetime import datetime, date
from src.finance.routers.reports_functions import get_coefficient_cession
from variables_for_backend import per_page_mov



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
async def get_expenses(page: int, cession_id: int = None, expenses_category_id: int = None, dates: List[str] = Query(None, alias="dates[]"), session: AsyncSession = Depends(get_async_session)):

    per_page = per_page_mov

    if dates and len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1

    elif dates and len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    try:
        if cession_id and expenses_category_id is None and date_1 is None:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id, expenses.c.status_pay == true())).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.status_pay == true()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.status_pay == true())))
        elif cession_id and expenses_category_id and date_1 is None:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.status_pay == true())).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                                            expenses.c.expenses_category_id == expenses_category_id,
                                                                                                            expenses.c.status_pay == true()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                               expenses.c.expenses_category_id == expenses_category_id,
                                                                                               expenses.c.status_pay == true())))
        elif cession_id and expenses_category_id and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                      expenses.c.status_pay == true())).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                                            expenses.c.expenses_category_id == expenses_category_id,
                                                                                                            expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                                            expenses.c.status_pay == true()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                               expenses.c.expenses_category_id == expenses_category_id,
                                                                                               expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                               expenses.c.status_pay == true())))
        elif cession_id and expenses_category_id is None and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                      expenses.c.status_pay == true())).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                                            expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                                            expenses.c.status_pay == true()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                               expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                               expenses.c.status_pay == true())))
        elif cession_id is None and expenses_category_id and date_1 is None:
            query = await session.execute(select(expenses).where(and_(expenses.c.expenses_category_id == expenses_category_id, expenses.c.status_pay == true())).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.expenses_category_id == expenses_category_id, expenses.c.status_pay == true()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == expenses_category_id, expenses.c.status_pay == true())))
        elif cession_id is None and expenses_category_id and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                      expenses.c.status_pay == true())).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                                                            expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                                            expenses.c.status_pay == true()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                                               expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                               expenses.c.status_pay == true())))
        elif cession_id is None and expenses_category_id is None and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                      expenses.c.status_pay == true())).
                                          order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                                            expenses.c.status_pay == true()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                               expenses.c.status_pay == true())))
        else:
            query = await session.execute(select(expenses).where(expenses.c.status_pay == true()).order_by(desc(expenses.c.date)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(expenses.c.status_pay == true())))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(expenses.c.status_pay == true()))

        total_item = total_item_query.scalar()
        summa_all = summa_query.scalar() / 100
        num_page_all = int(math.ceil(total_item / per_page))

        data_expenses = []

        for item in query.mappings().all():

            summa_expenses = 0
            cession_id = None
            cession_name = None
            date_pay = None
            date_accrual = None

            expenses_category_query = await session.execute(select(ref_expenses_category).where(ref_expenses_category.c.id == int(item.expenses_category_id)))
            expenses_category_set = expenses_category_query.mappings().fetchone()

            if item.cession_id:
                cession_query = await session.execute(select(cession).where(cession.c.id == int(item.cession_id)))
                cession_set = cession_query.mappings().fetchone()
                cession_id = cession_set.id
                cession_name = cession_set.name

            if item.summa:
                summa_expenses = item.summa / 100

            if item.date:
                date_pay = datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_accrual:
                date_accrual = datetime.strptime(str(item.date_accrual), '%Y-%m-%d').strftime("%d.%m.%Y")

            data_expenses.append({
                "id": item.id,
                "datePay": date_pay,
                "dateAccrual": date_accrual,
                "summaPay": summa_expenses,
                "expenses_category_id": expenses_category_set.id,
                "expenses_category": expenses_category_set.name,
                "purposePay": item.payment_purpose,
                "cession_id": cession_id,
                "cession_name": cession_name,
                "statusPay": item.status_pay,

            })

        result = {'data_expenses': data_expenses,
                  'summa_all': summa_all,
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
    result = await calculation_expenses(req_data, session)

    return result



# Добавить расходы организации списком
router_save_expenses_list = APIRouter(
    prefix="/v1/SaveExpensesList",
    tags=["Finance"]
)


@router_save_expenses_list.post("/")
async def save_expenses_list(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    req_data = data_json['data']
    result = await calculation_expenses(req_data, session)

    return result


async def calculation_expenses(req_data, session):

    try:
        for data in req_data:
            if data['cession_id'] and data['expenses_category_id'] is None:
                return {
                    "status": "error",
                    "data": None,
                    "details": f"Не назначена категория платежа для суммы {data['summaPay']} от {data['datePay']}"
                }

            if data['cession_id'] == 99999:
                cession_query = await session.execute(select(cession.c.id))

                for item in cession_query.mappings().all():
                    cession_id: int = item['id']

                    data_coefficient = await get_coefficient_cession(cession_id,  session)
                    coefficient_cession = data_coefficient['coefficient_cession']
                    summa = int(float(data['summaPay']) * coefficient_cession)

                    if summa > 0:

                        data_pay = {
                            "id": None,
                            "datePay": data['datePay'],
                            "dateAccrual": data['dateAccrual'],
                            "summaPay": summa,
                            "expenses_category_id": data['expenses_category_id'],
                            "purposePay": data['purposePay'],
                            "cession_id": cession_id,
                            "statusPay": data['statusPay']
                        }
                        await save_expenses(data_pay, session)
            elif data['cession_id'] and data['cession_id'] != 99999:
                await save_expenses(data, session)
            else:
                pass
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }

    return {
        'status': 'success',
        'data': None,
        'details': 'Расход успешно сохранен'
    }


# Получить начисленные расходы организации
router_accrual_expenses = APIRouter(
    prefix="/v1/AccrualExpenses",
    tags=["Finance"]
)


@router_accrual_expenses.get("/")
async def get_accrual_expenses(page: int, cession_id: int = None, expenses_category_id: int = None, dates: List[str] = Query(None, alias="dates[]"), session: AsyncSession = Depends(get_async_session)):

    per_page = per_page_mov

    if dates and len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1

    elif dates and len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    try:
        if cession_id and expenses_category_id is None and date_1 is None:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id, expenses.c.status_pay == false())).
                                          order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.status_pay == false()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.status_pay == false())))
        elif cession_id and expenses_category_id and date_1 is None:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.status_pay == false())).
                                          order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                                            expenses.c.expenses_category_id == expenses_category_id,
                                                                                                            expenses.c.status_pay == false()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                               expenses.c.expenses_category_id == expenses_category_id,
                                                                                               expenses.c.status_pay == false())))
        elif cession_id and expenses_category_id and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                      expenses.c.status_pay == false())).
                                          order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                                            expenses.c.expenses_category_id == expenses_category_id,
                                                                                                            expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                                            expenses.c.status_pay == false()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                               expenses.c.expenses_category_id == expenses_category_id,
                                                                                               expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                               expenses.c.status_pay == false())))
        elif cession_id and expenses_category_id is None and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.cession_id == cession_id,
                                                                      expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                      expenses.c.status_pay == false())).
                                          order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                                            expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                                            expenses.c.status_pay == false()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id,
                                                                                               expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                               expenses.c.status_pay == false())))
        elif cession_id is None and expenses_category_id and date_1 is None:
            query = await session.execute(select(expenses).where(and_(expenses.c.expenses_category_id == expenses_category_id, expenses.c.status_pay == false())).
                                          order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.expenses_category_id == expenses_category_id, expenses.c.status_pay == false()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == expenses_category_id, expenses.c.status_pay == false())))
        elif cession_id is None and expenses_category_id and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                      expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                      expenses.c.status_pay == false())).
                                          order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                                                            expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                                            expenses.c.status_pay == false()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == expenses_category_id,
                                                                                               expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                               expenses.c.status_pay == false())))
        elif cession_id is None and expenses_category_id is None and date_1:
            query = await session.execute(select(expenses).where(and_(expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                      expenses.c.status_pay == false())).
                                          order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(and_(expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                                            expenses.c.status_pay == false()))))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                               expenses.c.status_pay == false())))
        else:
            query = await session.execute(select(expenses).where(expenses.c.status_pay == false()).order_by(desc(expenses.c.date_accrual)).order_by(desc(expenses.c.id)).
                                          limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(expenses.c.id)).filter(expenses.c.status_pay == false())))
            summa_query = await session.execute(select(func.sum(expenses.c.summa)).filter(expenses.c.status_pay == false()))

        total_item = total_item_query.scalar()
        summa_all = summa_query.scalar() / 100
        num_page_all = int(math.ceil(total_item / per_page))

        data_expenses = []

        for item in query.mappings().all():

            summa_expenses = 0
            cession_id = None
            cession_name = None
            date_pay = None
            date_accrual = None

            expenses_category_query = await session.execute(select(ref_expenses_category).where(ref_expenses_category.c.id == int(item.expenses_category_id)))
            expenses_category_set = expenses_category_query.mappings().fetchone()

            if item.cession_id:
                cession_query = await session.execute(select(cession).where(cession.c.id == int(item.cession_id)))
                cession_set = cession_query.mappings().fetchone()
                cession_id = cession_set.id
                cession_name = cession_set.name

            if item.summa:
                summa_expenses = item.summa / 100

            if item.date:
                date_pay = datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_accrual:
                date_accrual = datetime.strptime(str(item.date_accrual), '%Y-%m-%d').strftime("%d.%m.%Y")

            data_expenses.append({
                "id": item.id,
                "datePay": date_pay,
                "dateAccrual": date_accrual,
                "summaPay": summa_expenses,
                "expenses_category_id": expenses_category_set.id,
                "expenses_category": expenses_category_set.name,
                "purposePay": item.payment_purpose,
                "cession_id": cession_id,
                "cession_name": cession_name,
                "statusPay": item.status_pay,
            })

        result = {'data_expenses': data_expenses,
                  'summa_all': summa_all,
                  'count_all': total_item,
                  'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


async def save_expenses(req_data, session):

    date_exp = None
    date_accrual = None
    summa = 0

    if req_data['datePay']:
        try:
            date_exp = datetime.strptime(req_data['datePay'], '%Y-%m-%d').date()
        except:
            date_exp = datetime.strptime(req_data['datePay'], '%d.%m.%Y').date()

    if req_data['dateAccrual']:
        try:
            date_accrual = datetime.strptime(req_data['dateAccrual'], '%Y-%m-%d').date()
        except:
            date_accrual = datetime.strptime(req_data['dateAccrual'], '%d.%m.%Y').date()

    if req_data['summaPay']:
        summa = int(float(req_data['summaPay']) * 100)

    if len(req_data['purposePay']) > 150:
        req_data['purposePay'] = req_data['purposePay'][:150]

    data = {
        "date": date_exp,
        "date_accrual": date_accrual,
        "summa": summa,
        "expenses_category_id": req_data['expenses_category_id'],
        "payment_purpose": req_data['purposePay'],
        "cession_id": req_data['cession_id'],
        "status_pay": req_data['statusPay'],
    }

    expenses_id: int = req_data["id"]
    if expenses_id:
        post_data = update(expenses).where(expenses.c.id == expenses_id).values(data)
    else:
        post_data = insert(expenses).values(data)

    await session.execute(post_data)
    await session.commit()