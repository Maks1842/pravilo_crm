import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor
from src.agreement.models import agreement


# Получить по credit_id/добавить соглашение
router_agreement = APIRouter(
    prefix="/v1/Agreement",
    tags=["Agreements"]
)


@router_agreement.get("/")
async def get_agreement(page: int, credit_id: int = None, cession_id: int = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page: int = 20

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
        if credit_id:
            agreement_query = await session.execute(select(agreement).where(agreement.c.credit_id == credit_id).
                                                  limit(per_page).offset((page - 1) * per_page))

            total_agrm_query = await session.execute(select(func.count(distinct(agreement.c.id)).filter(agreement.c.credit_id == credit_id)))
        elif credit_id == None and cession_id and dates1 == None:
            agreement_query = await session.execute(select(agreement).where(agreement.c.credit_id.in_(credits_id_list)).
                                                  limit(per_page).offset((page - 1) * per_page))

            total_agrm_query = await session.execute(select(func.count(distinct(agreement.c.id)).filter(agreement.c.credit_id.in_(credits_id_list))))
        elif credit_id == None and cession_id and dates1:
            agreement_query = await session.execute(select(agreement).where(and_(agreement.c.date >= dates1, agreement.c.date <= dates2, agreement.c.credit_id.in_(credits_id_list))).
                                                  limit(per_page).offset((page - 1) * per_page))

            total_agrm_query = await session.execute(select(func.count(distinct(agreement.c.id)).filter(and_(agreement.c.date >= dates1, agreement.c.date <= dates2, agreement.c.credit_id.in_(credits_id_list)))))
        elif credit_id == None and cession_id == None and dates1:
            agreement_query = await session.execute(select(agreement).where(and_(agreement.c.date >= dates1, agreement.c.date <= dates2)).
                                                  limit(per_page).offset((page - 1) * per_page))

            total_agrm_query = await session.execute(select(func.count(distinct(agreement.c.id)).filter(and_(agreement.c.date >= dates1, agreement.c.date <= dates2))))
        else:
            agreement_query = await session.execute(select(agreement).
                                                  limit(per_page).offset((page - 1) * per_page))

            total_agrm_query = await session.execute(select(func.count(distinct(agreement.c.id))))

        total_agrm = total_agrm_query.scalar()
        num_page_all = int(math.ceil(total_agrm / per_page))

        data_agreement = []
        for item in agreement_query.mappings().all():

            credit_id: int = item.credit_id
            credits_query = await session.execute(select(credit).where(credit.c.id == credit_id))
            credit_set = credits_query.mappings().one()
            debtor_id: int = credit_set.debtor_id

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()

            if debtor_item.last_name_2 is not None:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                             f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            text_payment_schedule = ''
            for pay_item in item.payment_schedule:
                if pay_item['datePay']:
                    payment_schedule = f"{pay_item['datePay'] or ''} - {pay_item['summaPay'] or ''}, "
                    text_payment_schedule = text_payment_schedule + payment_schedule

            data_agreement.append({
                "id": item.id,
                "credit_id": item.credit_id,
                "credit_num": credit_set.number,
                "debtor_id": debtor_item.id,
                "debtor_name": debtor_fio,
                "date_agreement": datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y"),
                "num_agreement": item.number,
                "summa_agreement": item.summa / 100,
                "text_payment_schedule": text_payment_schedule,
                "payment_schedule": item.payment_schedule,
                "comment": item.comment,
            })

        result = {'data_agreement': data_agreement,
                  'count_all': total_agrm,
                  'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_agreement.post("/")
async def add_agreement(data: dict, session: AsyncSession = Depends(get_async_session)):

    if data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }

    date_agreement = date.today()
    summa = 0

    if data['date_agreement'] is not None:
        date_agreement = datetime.strptime(data['date_agreement'], '%Y-%m-%d').date()
    if data['summa_agreement'] is not None:
        summa = int(float(data['summa_agreement']) * 100)

    try:
        agreement_data = {
            "credit_id": data["credit_id"],
            "date": date_agreement,
            "number": data['num_agreement'],
            "summa": summa,
            "payment_schedule": data['payment_schedule'],
            "comment": data['comment']
        }

        if data["id"]:
            agr_id: int = data["id"]
            post_data = update(agreement).where(agreement.c.id == agr_id).values(agreement_data)
        else:
            post_data = insert(agreement).values(agreement_data)

        await session.execute(post_data)
        await session.commit()
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }

    return {
        'status': 'success',
        'data': None,
        'details': f'Соглашение успешно сохранено'
    }
