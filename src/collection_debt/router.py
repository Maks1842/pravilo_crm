from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import *
from src.collection_debt.schemas import EDocCreate



router_ed_debtor = APIRouter(
    prefix="/EDocDebtor",
    tags=["collection_debt"]
)


# Получить информацию об ИД
@router_ed_debtor.get("/")
async def get_ed_debtor(credit_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(executive_document).where(executive_document.c.credit_id == credit_id)

        answer = await session.execute(query)
        print(answer)

        result = []
        for item in answer.all():
            print(item)
            data = dict(item._mapping)
            print(data)


            status_query = await session.execute(select(ref_status_credit).where(ref_status_credit.c.id == int(data['status_cd_id'])))
            status_set = dict(status_query.one()._mapping)
            status = status_set['name']

            result.append({
                'id': data['id'],
                'debtor_id': data['debtor_id'],
                'status_cd': status,
                'status_cd_id': data['status_cd_id'],
                'creditor': data['creditor'],
                'number': data['number'],
                'date_start': data['date_start'],
                'date_end': data['date_end'],
                'summa': data['summa'],
                'summa_by_cession': data['summa_by_cession'],
                'interest_rate': data['interest_rate'],
                'percent_of_od': data['percent_of_od'],
                'overdue_od': data['overdue_od'],
                'overdue_percent': data['overdue_percent'],
                'penalty': data['penalty'],
                'gov_toll': data['gov_toll'],
                'cession_id': data['cession_id'],
                'balance_debt': data['balance_debt'],
                'credits_old': data['credits_old'],
                'comment': data['comment'],
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


# Изменить данные об ИД
@router_ed_debtor.post("/")
async def add_ed_debtor(new_ed_debtor: EDocCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_ed_debtor.model_dump()

    try:
        if req_data["id"]:
            ed_id = int(req_data["id"])
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
                "summa_debt_decision": req_data["summa_debt_decision"],
                "state_duty": req_data["state_duty"],
                "succession": req_data["succession"],
                "date_entry_force": req_data["date_entry_force"],
                "claimer_ed_id": req_data['claimer_ed_id'],
                "tribunal_id": req_data["tribunal_id"],
                "comment": req_data["comment"],
            }

            # Не срабатывает исключение, если нет указанного id в БД
            post_data = update(executive_document).where(executive_document.c.id == ed_id).values(data)
        else:
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
                "summa_debt_decision": req_data["summa_debt_decision"],
                "state_duty": req_data["state_duty"],
                "succession": req_data["succession"],
                "date_entry_force": req_data["date_entry_force"],
                "claimer_ed_id": req_data['claimer_ed_id'],
                "tribunal_id": req_data["tribunal_id"],
                "comment": req_data["comment"],
            }
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