import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.payments.models import payment
from src.collection_debt.models import executive_document
from src.auth.models import user


# Получить по credit_id/добавить платежи
router_payment = APIRouter(
    prefix="/v1/Payments",
    tags=["Payments"]
)


@router_payment.get("/")
async def get_payment(page: int, credit_id: int = None, cession_id: int = None, department_pay: str = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):
    per_page = 20

    if dates2 is None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    credits_id_list = []
    if cession_id:
        credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
        credits_id_list = credits_id_query.scalars().all()

    try:
        if credit_id == None and dates1 and department_pay == None and cession_id == None:
            payment_query = await session.execute(select(payment).where(and_(payment.c.date >= dates1, payment.c.date <= dates2)).
                                               order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))

            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(and_(payment.c.date >= dates1, payment.c.date <= dates2)))
            summa_all = summa_query.scalar() / 100
        elif credit_id and dates1 == None and department_pay == None and cession_id == None:
            payment_query = await session.execute(select(payment).where(payment.c.credit_id == credit_id).
                                               order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(payment.c.credit_id == credit_id))
            summa_all = summa_query.scalar() / 100
        elif credit_id and dates1 and department_pay == None and cession_id == None:
            payment_query = await session.execute(select(payment).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.credit_id == credit_id)).
                                                  order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.credit_id == credit_id)))
            summa_all = summa_query.scalar() / 100
        elif dates1 == None and department_pay and cession_id == None:
            payment_query = await session.execute(select(payment).where(payment.c.comment.icontains(department_pay)).
                                               order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(payment.c.comment.icontains(department_pay)))
            summa_all = summa_query.scalar() / 100
        elif dates1 and department_pay and cession_id == None:
            payment_query = await session.execute(select(payment).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.comment.icontains(department_pay))).
                                                  order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.comment.icontains(department_pay))))
            summa_all = summa_query.scalar() / 100
        elif dates1 == None and department_pay == None and cession_id:
            payment_query = await session.execute(select(payment).where(payment.c.credit_id.in_(credits_id_list)).
                                               order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(payment.c.credit_id.in_(credits_id_list)))
            summa_all = summa_query.scalar() / 100
        elif dates1 and department_pay == None and cession_id:
            payment_query = await session.execute(select(payment).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.credit_id.in_(credits_id_list))).
                                                  order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.credit_id.in_(credits_id_list))))
            summa_all = summa_query.scalar() / 100
        elif dates1 and department_pay and cession_id:
            payment_query = await session.execute(select(payment).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.credit_id.in_(credits_id_list), payment.c.comment.icontains(department_pay))).
                                                  order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(and_(payment.c.date >= dates1, payment.c.date <= dates2, payment.c.credit_id.in_(credits_id_list), payment.c.comment.icontains(department_pay))))
            summa_all = summa_query.scalar() / 100
        elif dates1 == None and department_pay and cession_id:
            payment_query = await session.execute(select(payment).where(and_(payment.c.credit_id.in_(credits_id_list), payment.c.comment.icontains(department_pay))).
                                                  order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(and_(payment.c.credit_id.in_(credits_id_list), payment.c.comment.icontains(department_pay))))
            summa_all = summa_query.scalar() / 100
        else:
            payment_query = await session.execute(select(payment).order_by(desc(payment.c.date)).order_by(desc(payment.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            summa_query = await session.execute(select(func.sum(payment.c.summa)))
            summa_all = summa_query.scalar() / 100

        query_set = payment_query.mappings().all()

        total_item = len(query_set)
        num_page_all = int(math.ceil(total_item / per_page))

        data_payment = []
        for item in query_set:

            debtor_fio = None
            credit_number = None
            cession_name = None

            credit_id: int = item.credit_id
            credits_query = await session.execute(select(credit).where(credit.c.id == credit_id))
            credit_set = credits_query.mappings().one()
            credit_number = credit_set.number
            debtor_id: int = credit_set.debtor_id
            cession_id: int = credit_set.cession_id

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()

            if debtor_item.last_name_2 is not None:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                             f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            if cession_id:
                cession_query = await session.execute(select(cession).where(cession.c.id == cession_id))
                cession_name = cession_query.scalar()

            data_payment.append({
                "id": item.id,
                "debtor_id": debtor.id,
                "debtorName": debtor_fio,
                "credit_id": credit_set.id,
                "creditNum": credit_set.number,
                "summa": item['summa'],
                "date": datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y"),
                "numPayDoc": item.payment_doc_num,
                "departmentPay": item.comment,
                "cession": cession_name,
                "cession_id": credit_set.cession_id,
            })

        result = {'data_payment': data_payment,
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


@router_payment.post("/")
async def add_payment(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']

    if data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }

    date = None
    summa = 0

    if data['date'] is not None:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if data['summa'] is not None:
        summa = int(float(data['summa']) * 100)

    try:
        pay_data = {
            "credit_id": data["credit_id"],
            "date": date,
            "summa": summa,
            "payment_doc_num": data['numPayDoc'],
            "comment": data['departmentPay']
        }

        if data["id"]:
            pay_id: int = data["id"]
            post_data = update(payment).where(payment.c.id == pay_id).values(pay_data)
        else:
            post_data = insert(payment).values(pay_data)

        await session.execute(post_data)
        await session.commit()

        result = await calculate_and_post_balance(data['credit_id'], summa, session)

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


async def calculate_and_post_balance(credit_id: int, summa, session):
    credits_query = await session.execute(select(credit).where(credit.c.id == credit_id))
    credit_set = credits_query.mappings().fetchone()

    try:
        ed_query = await session.execute(select(executive_document.c.summa_debt_decision).where(executive_document.c.credit_id == credit_id))
        summa_debt_decision = ed_query.scalar()

        summa_query = await session.execute(select(func.sum(payment.c.summa)))
        summa_all = summa_query.scalar()

        if summa_all:
            summa_pay = summa_all
        else:
            summa_pay = 0
        balance_debt = summa_debt_decision - summa_pay
    except:
        balance_debt = credit_set.balance_debt - summa

    try:
        post_data = update(credit).where(credit.c.id == credit_id).values(balance_debt)

        await session.execute(post_data)
        await session.commit()
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при изменении баланса. Платеж сохранен, но баланс не изменен. {ex}"
        }

    return {
        'status': 'success',
        'data': None,
        'details': 'Платеж успешно сохранен. Остаток долга успешно изменен'
    }