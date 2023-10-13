import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import *
from src.collection_debt.schemas import EDocCreate
from src.references.models import ref_rosp, ref_bank, ref_pfr, ref_type_department



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
                'executive_document_id': item.id,
                'number': item.number,
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить департаменты предъявления ИД
router_department_presentation = APIRouter(
    prefix="/v1/GetDepartmentPresentation",
    tags=["Collection_debt"]
)


@router_department_presentation.get("/")
async def get_department_presentation(type_department_id: int, fragment: str, session: AsyncSession = Depends(get_async_session)):
    try:
        if type_department_id == 1:
            department_query = await session.execute(select(ref_rosp).where(ref_rosp.c.name.icontains(fragment)))
        elif type_department_id == 2:
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


@router_collection_debt.get("/")
async def get_collection_debt(page: int, credit_id: int = None, type_department_id: int = None, department_id: int = None, dates1: str = None, dates2: str = None, ed_id: int = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20

    if dates2 is None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    try:
        if credit_id:
            collect_query = await session.execute(select(collection_debt).where(collection_debt.c.credit_id == credit_id).
                                               order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.credit_id == credit_id))
        elif ed_id:
            collect_query = await session.execute(select(collection_debt).where(collection_debt.c.executive_document_id == ed_id).
                                                  order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.executive_document_id == ed_id))
        elif credit_id == None and ed_id == None and dates1 and department_id == None and type_department_id == None:
            collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2)).
                                                  order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2)))
        elif credit_id == None and ed_id == None and dates1 == None and department_id == None and type_department_id:
            collect_query = await session.execute(select(collection_debt).where(collection_debt.c.type_department_id == type_department_id).
                                                  order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.type_department_id == type_department_id))
        elif credit_id == None and ed_id == None and dates1 and department_id == None and type_department_id:
            collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                     collection_debt.c.date_start <= dates2,
                                                                                     collection_debt.c.type_department_id == type_department_id)).
                                                  order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                       collection_debt.c.date_start <= dates2,
                                                                                                                       collection_debt.c.type_department_id == type_department_id)))
        elif credit_id == None and ed_id == None and dates1 == None and department_id:
            collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                     collection_debt.c.type_department_id == type_department_id)).
                                                  order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                       collection_debt.c.type_department_id == type_department_id)))
        elif credit_id == None and ed_id == None and dates1 and department_id:
            collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                     collection_debt.c.date_start <= dates2,
                                                                                     collection_debt.c.department_presentation_id == department_id,
                                                                                     collection_debt.c.type_department_id == type_department_id)).
                                                  order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                                  limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                       collection_debt.c.date_start <= dates2,
                                                                                                                       collection_debt.c.department_presentation_id == department_id,
                                                                                                                       collection_debt.c.type_department_id == type_department_id)))
        else:
            collect_query = await session.execute(select(collection_debt).order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))))

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
            "date_return": date_end,
            "date_end": date_return,
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