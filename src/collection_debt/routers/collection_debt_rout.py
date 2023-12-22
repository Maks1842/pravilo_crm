import math
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import *
from src.references.models import ref_rosp, ref_bank, ref_pfr, ref_type_department
from src.registries.models import registry_filters
from src.collection_debt.routers.collection_debt_functions import get_collection_debt_all
import src.collection_debt.routers.collection_debt_functions as collection_functions
from variables_for_backend import per_page_reg, VarTypeDep


# Получить департаменты предъявления ИД
router_department_presentation = APIRouter(
    prefix="/v1/GetDepartmentPresentation",
    tags=["Collection_debt"]
)


@router_department_presentation.get("/")
async def get_department_presentation(type_department_id: int, fragment: str, session: AsyncSession = Depends(get_async_session)):
    try:
        if type_department_id == VarTypeDep.type_rosp:
            department_query = await session.execute(select(ref_rosp).where(ref_rosp.c.name.icontains(fragment)))
        elif type_department_id == VarTypeDep.type_bank:
            department_query = await session.execute(select(ref_bank).where(ref_bank.c.name.icontains(fragment)))
        else:
            department_query = await session.execute(select(ref_pfr).where(ref_pfr.c.name.icontains(fragment)))

        result = []
        for item in department_query.mappings().all():

            result.append({
                "department_presentation": item.name,
                "value": {"department_presentation_id": item.id},
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Движение ИД
router_collection_debt = APIRouter(
    prefix="/v1/CollectionDebt",
    tags=["Collection_debt"]
)


@router_collection_debt.post("/")
async def get_collection_debt(data: dict, session: AsyncSession = Depends(get_async_session)):

    print(f'main {data}')

    per_page = per_page_reg
    filter_id: int = data['filter_id']


    try:
        if filter_id:
            filter_query = await session.execute(select(registry_filters).where(registry_filters.c.id == filter_id))
            filter_set = filter_query.mappings().fetchone()
            functions_control = getattr(collection_functions, f'{filter_set.function_name}')
            coll_deb_set = await functions_control(per_page, data, session)
        else:
            coll_deb_set = await get_collection_debt_all(per_page, data, session)

        total_collect_query = coll_deb_set['total_collect_query']
        collect_query = coll_deb_set['collect_query']

        total_item = total_collect_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_collect = []
        for item in collect_query.mappings().all():

            type_department = None
            type_department_id = None
            department_presentation = None
            department_presentation_id = None
            department_address = None
            ed_number = None
            executive_document_id = None
            reason_cansel = None
            reason_cansel_id = None
            date_return = None
            date_end = None

            credit_id: int = item.credit_id
            credits_query = await session.execute(select(credit).where(credit.c.id == credit_id))
            credit_set = credits_query.mappings().one()
            credit_number = credit_set.number
            debtor_id: int = credit_set.debtor_id

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()

            if debtor_item.last_name_2 is not None:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                             f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            if item.type_department_id is not None:
                type_department_query = await session.execute(select(ref_type_department.c.name).where(ref_type_department.c.id == int(item.type_department_id)))
                type_department = type_department_query.scalar()
                type_department_id = item.type_department_id

                if item.type_department_id == 1:
                    department_query = await session.execute(select(ref_rosp).where(ref_rosp.c.id == int(item.department_presentation_id)))
                elif item.type_department_id == 2:
                    department_query = await session.execute(select(ref_bank).where(ref_bank.c.id == int(item.department_presentation_id)))
                else:
                    department_query = await session.execute(select(ref_pfr).where(ref_pfr.c.id == int(item.department_presentation_id)))

                department_set = department_query.mappings().fetchone()
                department_presentation = department_set.name
                department_presentation_id = department_set.id
                department_address = f"{department_set.address_index or ''}, {department_set.address}"

            if item.executive_document_id is not None:
                ed_query = await session.execute(select(executive_document.c.number).where(executive_document.c.id == int(item.executive_document_id)))
                ed_number = ed_query.scalar()
                executive_document_id = item.executive_document_id

            if item.reason_cansel_id is not None:
                reason_cansel_query = await session.execute(select(ref_reason_cansel_ed.c.name).where(ref_reason_cansel_ed.c.id == int(item.reason_cansel_id)))
                reason_cansel = reason_cansel_query.scalar()
                reason_cansel_id = item.reason_cansel_id

            if item.date_return is not None:
                date_return = datetime.strptime(str(item.date_return), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_end is not None:
                date_end = datetime.strptime(str(item.date_end), '%Y-%m-%d').strftime("%d.%m.%Y")

            data_collect.append({
                "id": item.id,
                "credit": credit_number,
                "credit_id": credit_id,
                "debtorName": debtor_fio,
                "type_department": type_department,
                "type_department_id": type_department_id,
                "department_presentation": department_presentation,
                "department_presentation_id": department_presentation_id,
                "department_address": department_address,
                "executive_document": ed_number,
                "executive_document_id": executive_document_id,
                "date_start": datetime.strptime(str(item.date_start), '%Y-%m-%d').strftime("%d.%m.%Y"),
                "date_return": date_return,
                "reason_cansel": reason_cansel,
                "reason_cansel_id": reason_cansel_id,
                "date_end": date_end,
                "comment": item.comment,
            })

        result = {'data_collect': data_collect,
                  'count_all': total_item,
                  'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_collection_debt.post("/")
async def add_collection_debt(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']

    date_start = None
    date_end = None
    date_return = None

    if data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }

    if data['date_start'] is not None:
        date_start = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
    if data['date_end'] is not None:
        date_end = datetime.strptime(data['date_end'], '%Y-%m-%d').date()
    if data['date_return'] is not None:
        date_return = datetime.strptime(data['date_return'], '%Y-%m-%d').date()

    try:
        collection_data = {
            "department_presentation_id": data["department_presentation_id"],
            "type_department_id": data["type_department_id"],
            "executive_document_id": data["executive_document_id"],
            "credit_id": data['credit_id'],
            "date_start": date_start,
            "date_return": date_return,
            "date_end": date_end,
            "reason_cansel_id": data['reason_cansel_id'],
            "comment": data["comment"],
        }

        if data["id"]:
            collection_id: int = data["id"]
            post_data = update(collection_debt).where(collection_debt.c.id == collection_id).values(collection_data)
        else:
            post_data = insert(collection_debt).values(collection_data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': f'Движение ИД успешно сохранено'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }