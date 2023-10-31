import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import *



router_ep_debtor = APIRouter(
    prefix="/v1/ExecutiveProductions",
    tags=["Collection_debt"]
)


# Получить информацию об ИП
@router_ep_debtor.get("/")
async def get_ep_debtor(credit_id: int = None, debtor_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            query = await session.execute(select(executive_productions).where(executive_productions.c.credit_id == credit_id).
                                          order_by(desc(executive_productions.c.date_on)))
            ep_list = query.mappings().all()
        else:
            query_credit_id = await session.execute(select(credit.c.id).where(credit.c.debtor_id == debtor_id))
            credits_id_list = query_credit_id.scalars().all()

            query = await session.execute(select(executive_productions).where(executive_productions.c.credit_id.in_(credits_id_list)).
                                          order_by(desc(executive_productions.c.date_on)))
            ep_list = query.mappings().all()

        result = []
        for item in ep_list:

            if len(item) > 0:
                reason_end = ''
                reason_end_id = None
                rosp_id = None
                rosp_name = ''
                rosp_address = ''
                class_code = ''
                ed_number = ''
                ed_id = None
                curent_debt = 0
                summa_debt = 0
                gov_toll = 0
                date_end = None
                date_request = None

                if item.curent_debt is not None:
                    curent_debt = item.curent_debt / 100

                if item.summa_debt is not None:
                    summa_debt = item.summa_debt / 100

                if item.gov_toll is not None:
                    gov_toll = item.gov_toll / 100

                if item.rosp_id is not None:
                    rosp_query = await session.execute(select(ref_rosp).where(ref_rosp.c.id == int(item.rosp_id)))
                    rosp = rosp_query.mappings().one()

                    rosp_id = item.rosp_id
                    rosp_name = rosp.name
                    rosp_address = rosp.address
                    class_code = rosp.class_code

                if item.reason_end_id is not None:
                    reason_end_query = await session.execute(select(ref_reason_end_ep.c.name).where(ref_reason_end_ep.c.id == int(item.reason_end_id)))

                    reason_end = reason_end_query.scalar()
                    reason_end_id = item.reason_end_id

                if item.executive_document_id is not None:
                    ed_query = await session.execute(select(executive_document.c.number).where(executive_document.c.id == int(item.executive_document_id)))

                    ed_number = ed_query.scalar()
                    ed_id = item.executive_document_id

                if item.date_end is not None:
                    date_end = datetime.strptime(str(item.date_end), '%Y-%m-%d').strftime("%d.%m.%Y")

                if item.date_request is not None:
                    date_request = datetime.strptime(str(item.date_request), '%Y-%m-%d').strftime("%d.%m.%Y")


                result.append({
                    "id": item.id,
                    "number": item.number,
                    "summary_case": item.summary_case,
                    "date_on": datetime.strptime(str(item.date_on), '%Y-%m-%d').strftime("%d.%m.%Y"),
                    "date_end": date_end,
                    "reason_end": reason_end,
                    "reason_end_id": reason_end_id,
                    "curent_debt": curent_debt,
                    "summa_debt": summa_debt,
                    "gov_toll": gov_toll,
                    "rosp": rosp_name,
                    "rosp_id": rosp_id,
                    "rosp_address": rosp_address,
                    "class_code": class_code,
                    "pristav": item.pristav,
                    "pristav_phone": item.pristav_phone,
                    "date_request": date_request,
                    "object_ep": item.object_ep,
                    "executive_document": ed_number,
                    "executive_document_id": ed_id,
                    "credit_id": item.credit_id,
                    "claimer": item.claimer,
                    "comment": item.comment,
                })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Изменить данные об ИП
@router_ep_debtor.post("/")
async def add_ep_debtor(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']

    date_on = None
    date_end = None
    date_request = None
    curent_debt = None
    summa_debt = None
    gov_toll = None

    if data['curent_debt'] is not None:
        curent_debt = int(float(data['curent_debt']) * 100)
    if data['summa_debt'] is not None:
        summa_debt = int(float(data['summa_debt']) * 100)
    if data['gov_toll'] is not None:
        gov_toll = int(float(data['gov_toll']) * 100)

    if data['date_on'] is not None:
        date_on = datetime.strptime(data['date_on'], '%Y-%m-%d').date()
    if data['date_end'] is not None:
        date_end = datetime.strptime(data['date_end'], '%Y-%m-%d').date()
    if data['date_request'] is not None:
        date_request = datetime.strptime(data['date_request'], '%Y-%m-%d').date()

    try:
        ep_data = {
            "number": data["number"],
            "summary_case": data["summary_case"],
            "date_on": date_on,
            "date_end": date_end,
            "reason_end_id": data["reason_end_id"],
            "curent_debt": curent_debt,
            "summa_debt": summa_debt,
            "gov_toll": gov_toll,
            "rosp_id": data["rosp_id"],
            "pristav": data["pristav"],
            "pristav_phone": data["pristav_phone"],
            "date_request": date_request,
            "object_ep": data["object_ep"],
            "executive_document_id": data['executive_document_id'],
            "credit_id": data["credit_id"],
            "claimer": data["claimer"],
            "comment": data["comment"],
        }
        if data["id"]:
            ep_id = int(data["id"])

            post_data = update(executive_productions).where(executive_productions.c.id == ep_id).values(ep_data)
        else:
            post_data = insert(executive_productions).values(ep_data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': data,
            'details': 'Исполнительное производство успешно сохранено'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }