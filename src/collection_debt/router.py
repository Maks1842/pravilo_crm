from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import *
from src.collection_debt.schemas import EDocCreate



router_ed_debtor = APIRouter(
    prefix="/v1/EDocDebtor",
    tags=["Collection_debt"]
)


# Получить информацию об ИД
@router_ed_debtor.get("/")
async def get_ed_debtor(credit_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = await session.execute(select(executive_document).where(executive_document.c.credit_id == credit_id))

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

                result.append({
                    'id': item.id,
                    'type_ed': type_ed_name,
                    'type_ed_id': type_ed_id,
                    'number': item.number,
                    'date': item.date,
                    'case_number': item.case_number,
                    'date_of_receipt_ed': item.date_of_receipt_ed,
                    'date_decision': item.date_decision,
                    'summa_debt_decision': summa_debt_decision,
                    'state_duty': state_duty,
                    'status_ed': status_name,
                    'status_ed_id': status_id,
                    'succession': item.succession,
                    'date_entry_force': item.date_entry_force,
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
async def add_ed_debtor(new_ed_debtor: EDocCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_ed_debtor.model_dump()

    summa_debt_decision = req_data["summa_debt_decision"] * 100
    state_duty = req_data["state_duty"] * 100

    try:
        data = {
            "number": req_data["number"],
            "date": req_data["date"],
            "case_number": req_data["case_number"],
            "date_of_receipt_ed": req_data["date_of_receipt_ed"],
            "date_decision": req_data["date_decision"],
            "type_ed_id": req_data["type_ed_id"],
            "status_ed_id": req_data['status_ed_id'],
            "credit_id": req_data["credit_id"],
            "user_id": req_data["user_id"],
            "summa_debt_decision": summa_debt_decision,
            "state_duty": state_duty,
            "succession": req_data["succession"],
            "date_entry_force": req_data["date_entry_force"],
            "claimer_ed_id": req_data['claimer_ed_id'],
            "tribunal_id": req_data["tribunal_id"],
            "comment": req_data["comment"],
        }
        if req_data["id"]:
            ed_id = int(req_data["id"])

            # Не срабатывает исключение, если нет указанного id в БД
            post_data = update(executive_document).where(executive_document.c.id == ed_id).values(data)
        else:
            post_data = insert(executive_document).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': data,
            'details': 'Исполнительный документ успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }