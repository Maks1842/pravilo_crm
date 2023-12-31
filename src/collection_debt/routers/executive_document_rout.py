import re
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import *
from src.payments.routers.payments import calculate_and_post_balance
from src.debts.router import func_save_debtor


router_ed_debtor = APIRouter(
    prefix="/v1/EDocDebtor",
    tags=["Collection_debt"]
)


# Получить информацию об ИД
@router_ed_debtor.get("/")
async def get_ed_debtor(credit_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = await session.execute(select(executive_document).where(executive_document.c.credit_id == credit_id).order_by(desc(executive_document.c.id)))

        result = []
        for item in query.mappings().all():

            if len(item) > 0:
                type_ed_name = ''
                type_ed_id = None
                claimer_ed_name = ''
                claimer_ed_id = None
                tribunal = ''
                tribunal_id = None
                address_tribunal = ''
                email_tribunal = ''
                phone_tribunal = ''
                status_name = ''
                status_id = None
                summa_debt_decision = 0
                state_duty = 0
                date_ed = None
                date_of_receipt_ed = None
                date_decision = None
                date_entry_force = None
                succession = None

                if item.summa_debt_decision is not None:
                    summa_debt_decision = item.summa_debt_decision / 100

                if item.state_duty is not None:
                    state_duty = item.state_duty / 100

                if item.type_ed_id is not None:
                    type_ed_query = await session.execute(select(ref_type_ed).where(ref_type_ed.c.id == int(item.type_ed_id)))
                    type_ed = type_ed_query.mappings().one()

                    type_ed_name = type_ed.name
                    type_ed_id = type_ed.id

                if item.claimer_ed_id is not None:
                    claimer_ed_query = await session.execute(select(ref_claimer_ed).where(ref_claimer_ed.c.id == int(item.claimer_ed_id)))
                    claimer_ed = claimer_ed_query.mappings().one()

                    claimer_ed_name = claimer_ed.name
                    claimer_ed_id = claimer_ed.id

                if item.tribunal_id is not None:
                    tribunal_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == int(item.tribunal_id)))
                    tribunal_set = tribunal_query.mappings().one()

                    tribunal_id = item.tribunal_id
                    tribunal = tribunal_set.name
                    address_tribunal = tribunal_set.address
                    email_tribunal = tribunal_set.email
                    phone_tribunal = tribunal_set.phone

                if item.status_ed_id is not None:
                    status_ed_query = await session.execute(select(ref_status_ed).where(ref_status_ed.c.id == int(item.status_ed_id)))
                    status_ed = status_ed_query.mappings().one()
                    status_name = status_ed.name
                    status_id = status_ed.id

                if item.date is not None:
                    date_ed = datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y")
                if item.date_of_receipt_ed is not None:
                    date_of_receipt_ed = datetime.strptime(str(item.date_of_receipt_ed), '%Y-%m-%d').strftime("%d.%m.%Y")
                if item.date_decision is not None:
                    date_decision = datetime.strptime(str(item.date_decision), '%Y-%m-%d').strftime("%d.%m.%Y")
                if item.date_entry_force is not None:
                    date_entry_force = datetime.strptime(str(item.date_entry_force), '%Y-%m-%d').strftime("%d.%m.%Y")
                if item.succession is not None:
                    succession = datetime.strptime(str(item.succession), '%Y-%m-%d').strftime("%d.%m.%Y")

                result.append({
                    'id': item.id,
                    'type_ed': type_ed_name,
                    'type_ed_id': type_ed_id,
                    'number': item.number,
                    'date': date_ed,
                    'case_number': item.case_number,
                    'date_of_receipt_ed': date_of_receipt_ed,
                    'date_decision': date_decision,
                    'summa_debt_decision': summa_debt_decision,
                    'state_duty': state_duty,
                    'status_ed': status_name,
                    'status_ed_id': status_id,
                    'succession': succession,
                    'date_entry_force': date_entry_force,
                    'claimer_ed': claimer_ed_name,
                    'claimer_ed_id': claimer_ed_id,
                    "tribunal": tribunal,
                    "tribunal_id": tribunal_id,
                    "address_tribunal": address_tribunal,
                    "email_tribunal": email_tribunal,
                    "phone_tribunal": phone_tribunal,
                    'comment': item.comment,
                })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Изменить данные об ИД
@router_ed_debtor.post("/")
async def add_ed_debtor(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    list_ed = data_json['data_json']

    for item in list_ed:
        date_ed = None
        date_of_receipt_ed = None
        date_decision = None
        succession = None
        date_entry_force = None
        summa_debt_decision = None
        state_duty = None

        credit_id: int = item["credit_id"]
        ed_id = item["id"]

        query = await session.execute(select(credit.c.debtor_id).where(credit.c.id == credit_id))
        debtor_id = query.scalar()

        ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.credit_id == credit_id).order_by(desc(executive_document.c.id)))
        ed_set = ed_query.mappings().first()

        if ed_set and ed_id is None:
            ed_id = ed_set.id

        try:
            if item['summa_debt_decision'] is not None:
                summa_debt_decision = int(float(item["summa_debt_decision"]) * 100)
        except:
            summa_debt_decision = None
        try:
            if item['state_duty'] is not None:
                state_duty = int(float(item["state_duty"]) * 100)
        except:
            state_duty = None

        if item['date_decision'] is not None:
            date_ed = datetime.strptime(item['date_decision'], '%Y-%m-%d').date()
        if item['date_of_receipt_ed'] is not None:
            date_of_receipt_ed = datetime.strptime(item['date_of_receipt_ed'], '%Y-%m-%d').date()
        if item['date_decision'] is not None:
            date_decision = datetime.strptime(item['date_decision'], '%Y-%m-%d').date()
        if item['succession'] is not None:
            succession = datetime.strptime(item['succession'], '%Y-%m-%d').date()
        if item['date_entry_force'] is not None:
            date_entry_force = datetime.strptime(item['date_entry_force'], '%Y-%m-%d').date()

        try:
            data = {
                "number": item["number"],
                "date": date_ed,
                "case_number": item["case_number"],
                "date_of_receipt_ed": date_of_receipt_ed,
                "date_decision": date_decision,
                "type_ed_id": item["type_ed_id"],
                "status_ed_id": item['status_ed_id'],
                "credit_id": credit_id,
                "user_id": item["user_id"],
                "summa_debt_decision": summa_debt_decision,
                "state_duty": state_duty,
                "succession": succession,
                "date_entry_force": date_entry_force,
                "claimer_ed_id": item['claimer_ed_id'],
                "tribunal_id": item["tribunal_id"],
                "comment": item["comment"],
            }

            await save_ed(ed_id, data, session)

            await calculate_and_post_balance(credit_id, session)

            data_tribun = {"tribunal_id": item["tribunal_id"]}
            await func_save_debtor(debtor_id, data_tribun, session)

        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f"Ошибка при добавлении/изменении данных. {ex}"
            }

    return {
        'status': 'success',
        'data': None,
        'details': 'Исполнительный документ успешно сохранен'
    }


# Получить номера ИД
router_ed_number = APIRouter(
    prefix="/v1/GetED",
    tags=["Collection_debt"]
)


@router_ed_number.get("/")
async def get_ed_number(credit_id: int = None, fragment: str = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            query = await session.execute(select(executive_document).where(executive_document.c.credit_id == credit_id))
        else:
            query = await session.execute(select(executive_document).where(executive_document.c.number.icontains(fragment)))

        result = []
        for item in query.mappings().all():

            result.append({
                'number': item.number,
                "value": {"item_id": item.id,
                          "model": 'executive_document',
                          "field": 'id'}
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить Суд из ИД по credit_id
router_tribunal_ed = APIRouter(
    prefix="/v1/GetTribunalED",
    tags=["Collection_debt"]
)


@router_tribunal_ed.get("/")
async def get_tribunal_ed(credit_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        tribunal_name = None

        ed_query = await session.execute(select(executive_document.c.id, executive_document.c.tribunal_id).where(executive_document.c.credit_id == credit_id).order_by(desc(executive_document.c.id)))
        ed_set = ed_query.mappings().first()

        tribunal_id = ed_set.tribunal_id

        if tribunal_id:
            tribunal_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == int(tribunal_id)))
            tribunal_item = tribunal_query.mappings().one()

            tribunal_name = tribunal_item.name

        result = {"tribunal": tribunal_name,
                  "value": {"ed_id": ed_set.id,
                            "tribunal_id": tribunal_id}}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


async def save_ed(ed_id, data, session):
    if ed_id:
        post_data = update(executive_document).where(executive_document.c.id == int(ed_id)).values(data)
    else:
        post_data = insert(executive_document).values(data)

    await session.execute(post_data)
    await session.commit()