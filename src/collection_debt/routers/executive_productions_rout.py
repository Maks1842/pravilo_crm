import math
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit
from src.collection_debt.models import *
from variables_for_backend import per_page_reg

from src.registries.models import registry_filters
from src.collection_debt.routers.executive_prod_functions import get_execut_prod_all
import src.collection_debt.routers.executive_prod_functions as control_filters


router_get_ep_debtor = APIRouter(
    prefix="/v1/GetExecutiveProductions",
    tags=["Collection_debt"]
)


# Получить информацию об ИП
@router_get_ep_debtor.post("/")
async def get_ep_debtor(data: dict, session: AsyncSession = Depends(get_async_session)):

    per_page = int(per_page_reg)
    filter_id: int = data['filter_id']

    try:
        if filter_id:
            filter_query = await session.execute(select(registry_filters).where(registry_filters.c.id == filter_id))
            filter_set = filter_query.mappings().fetchone()
            functions_control = getattr(control_filters, f'{filter_set.function_name}')
            ep_set = await functions_control(per_page, data, session)

        else:
            ep_set = await get_execut_prod_all(per_page, data, session)

        total_ep_query = ep_set['total_ep_query']
        ep_query = ep_set['ep_query']

        total_item = total_ep_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_ep = []
        for item in ep_query.mappings().all():

            if len(item) > 0:
                reason_end = ''
                reason_end_id = None
                rosp_id = None
                rosp_name = ''
                rosp_address = ''
                class_code = ''
                ed_number = ''
                ed_id = None
                ed_type_id = None
                ed_type_name = ''
                curent_debt = 0
                summa_debt = 0
                gov_toll = 0
                date_on = None
                date_end = None
                date_request = None

                credit_id: int = item.credit_id
                credits_query = await session.execute(select(credit).where(credit.c.id == credit_id))
                credit_set = credits_query.mappings().one()
                credit_number = credit_set.number
                debtor_id: int = credit_set.debtor_id
                cession_id: int = credit_set.cession_id

                cession_query = await session.execute(select(cession.c.name).where(cession.c.id == cession_id))
                cession_name = cession_query.scalar()

                debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
                debtor_item = debtor_query.mappings().one()

                if debtor_item.last_name_2 is not None:
                    debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                                 f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
                else:
                    debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

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
                    ed_query = await session.execute(select(executive_document).where(executive_document.c.id == int(item.executive_document_id)))
                    ed_set = ed_query.mappings().one()

                    ed_id = ed_set.id
                    ed_number = ed_set.number
                    ed_type_id: int = ed_set.type_ed_id

                    ed_type_query = await session.execute(select(ref_type_ed.c.name).where(ref_type_ed.c.id == ed_type_id))
                    ed_type_name = ed_type_query.scalar()


                if item.date_on is not None:
                    date_on = datetime.strptime(str(item.date_on), '%Y-%m-%d').strftime("%d.%m.%Y")
                if item.date_end is not None:
                    date_end = datetime.strptime(str(item.date_end), '%Y-%m-%d').strftime("%d.%m.%Y")
                if item.date_request is not None:
                    date_request = datetime.strptime(str(item.date_request), '%Y-%m-%d').strftime("%d.%m.%Y")


                data_ep.append({
                    "id": item.id,
                    "credit": credit_number,
                    "credit_id": credit_id,
                    "cession": cession_name,
                    "cession_id": cession_id,
                    "debtorName": debtor_fio,
                    "number": item.number,
                    "summary_case": item.summary_case,
                    "date_on": date_on,
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
                    "ed_type": ed_type_name,
                    "ed_type_id": ed_type_id,

                    "claimer": item.claimer,
                    "comment": item.comment,
                })

        result = {'data_ep': data_ep,
                  'count_all': total_item,
                  'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


router_save_ep_debtor = APIRouter(
    prefix="/v1/SaveExecutiveProductions",
    tags=["Collection_debt"]
)


# Изменить данные об ИП
@router_save_ep_debtor.post("/")
async def add_ep_debtor(data: dict, session: AsyncSession = Depends(get_async_session)):

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


# Получить номера ИП
router_ep_number = APIRouter(
    prefix="/v1/GetEP",
    tags=["Collection_debt"]
)


@router_ep_number.get("/")
async def get_ep_number(credit_id: int = None, fragment: str = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            query = await session.execute(select(executive_productions).where(executive_productions.c.credit_id == credit_id))
        else:
            query = await session.execute(select(executive_productions).where(executive_productions.c.number.icontains(fragment)))

        result = []
        for item in query.mappings().all():

            result.append({
                'number': item.number,
                "value": {"item_id": item.id,
                          "model": 'executive_productions',
                          "field": 'id'}
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }