import math
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, distinct, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.legal_work.models import legal_work
from src.legal_work.routers.helper_legal_work import number_case_legal, save_case_legal
from src.references.models import ref_legal_docs, ref_result_statement, ref_tribunal
from variables_for_backend import per_page_legal

'''
Метод для судебной работы
'''


# Получить/добавить 208
router_tribunal_208 = APIRouter(
    prefix="/v1/Tribun208",
    tags=["LegalWork"]
)


@router_tribunal_208.get("/")
async def get_tribunal_208(page: int, credit_id: int = None, cession_id: int = None, legal_section_id: int = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page = int(per_page_legal)

    if dates2 is None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    try:
        if credit_id:
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id == credit_id)).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(legal_work.c.id)).filter(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id == credit_id))))
        elif credit_id == None and cession_id == None and dates1:
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.date_result_1 >= dates1, legal_work.c.date_result_1 <= dates2)).
                                               order_by(desc(legal_work.c.legal_number)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(legal_work.c.id)).filter(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.date_result_1 >= dates1, legal_work.c.date_result_1 <= dates2))))
        elif credit_id == None and cession_id and dates1 == None:
            credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
            credits_id_list = credits_id_query.scalars().all()
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list))).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(legal_work.c.id)).filter(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list)))))
        elif credit_id == None and cession_id and dates1:
            credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
            credits_id_list = credits_id_query.scalars().all()
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list), legal_work.c.date_result_1 >= dates1, legal_work.c.date_result_1 <= dates2)).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(legal_work.c.id)).filter(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list), legal_work.c.date_result_1 >= dates1, legal_work.c.date_result_1 <= dates2))))
        else:
            legal_query = await session.execute(select(legal_work).where(legal_work.c.legal_section_id == legal_section_id).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(select(func.count(distinct(legal_work.c.id)).filter(legal_work.c.legal_section_id == legal_section_id)))

        total_item = total_item_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_legal = []
        for item in legal_query.mappings().all():

            credit_id: int = item.credit_id

            legal_docs = ''
            legal_docs_id = None
            result_1 = ''
            result_1_id = None
            summa_claim = None
            date_session_1 = None
            date_result_1 = None
            date_incoming_ed = None
            date_entry_force = None
            date_stop_case = None
            tribunal_1 = ''
            tribunal_1_id = None
            address_tribunal_1 = ''
            email_tribunal_1 = ''
            phone_tribunal_1 = ''
            gaspravosudie = 'НЕ возможно'

            credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
            credit_set = credit_query.mappings().one()
            cession_id: int = credit_set.cession_id

            cession_query = await session.execute(select(cession).where(cession.c.id == cession_id))
            cession_set = cession_query.mappings().one()

            debtor_id: int = credit_set.debtor_id

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()

            if debtor_item.last_name_2 is not None:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                             f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            if item.legal_docs_id is not None:
                name_task_query = await session.execute(select(ref_legal_docs.c.name).where(ref_legal_docs.c.id == int(item.legal_docs_id)))
                legal_docs = name_task_query.scalar()
                legal_docs_id = item.legal_docs_id

            if item.result_1_id is not None:
                result_1_id: int = item.result_1_id
                result_1_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == result_1_id))
                result_1 = result_1_query.scalar()

            if item.summa_claim is not None:
                summa_claim = item.summa_claim / 100

            if item.date_session_1 is not None:
                date_session_1 = datetime.strptime(str(item.date_session_1), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_result_1 is not None:
                date_result_1 = datetime.strptime(str(item.date_result_1), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_incoming_ed is not None:
                date_incoming_ed = datetime.strptime(str(item.date_incoming_ed), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_entry_force is not None:
                date_entry_force = datetime.strptime(str(item.date_entry_force), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_stop_case is not None:
                date_stop_case = datetime.strptime(str(item.date_stop_case), '%Y-%m-%d').strftime("%d.%m.%Y")

            if item.tribunal_1_id is not None:
                tribunal_1_id: int = item.tribunal_1_id
                tribunal_1_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == tribunal_1_id))
                tribunal_1_set = tribunal_1_query.mappings().one()

                tribunal_1 = tribunal_1_set.name
                address_tribunal_1 = tribunal_1_set.address
                email_tribunal_1 = tribunal_1_set.email
                phone_tribunal_1 = tribunal_1_set.phone
                if tribunal_1_set.gaspravosudie == True:
                    gaspravosudie = 'Возможно'

            data_legal.append({
                "id": item.id,
                "legalNumber": item.legal_number,
                "legalSection_id": item.legal_section_id,
                "credit_id": item.credit_id,
                "credit": credit_set.number,
                "cession_id": cession_set.id,
                "cessionName": cession_set.name,
                "debtorName": debtor_fio,
                "numberCase_1": item.number_case_1,
                "legalDocs": legal_docs,
                "legalDocs_id": legal_docs_id,
                "dateSession_1": date_session_1,
                "dateResult_1": date_result_1,
                "result_1": result_1,
                "result_1_id": result_1_id,
                "summaClaim": summa_claim,
                "dateIncomingED": date_incoming_ed,
                "dateEntryIntoForce": date_entry_force,
                "tribun_1": tribunal_1,
                "tribun_1_id": tribunal_1_id,
                "addressTribun_1": address_tribunal_1,
                "emailTribun_1": email_tribunal_1,
                "phoneTribun_1": phone_tribunal_1,
                "dateStopCase": date_stop_case,
                "comment": item.comment,
                "gaspravosudie": gaspravosudie,
            })

        result = {'data_legal': data_legal,
                  'count_all': total_item,
                  'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_tribunal_208.post("/")
async def add_tribunal_208(data: dict, session: AsyncSession = Depends(get_async_session)):

    if data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }
    date_session_1 = None
    date_result_1 = None
    date_entry_force = None
    date_incoming_ed = None
    date_stop_case = None
    summa_claim = 0

    if data['dateSession_1'] is not None:
        date_session_1 = datetime.strptime(data['dateSession_1'], '%Y-%m-%d').date()
    if data['dateResult_1'] is not None:
        date_result_1 = datetime.strptime(data['dateResult_1'], '%Y-%m-%d').date()
    if data['dateEntryIntoForce'] is not None:
        date_entry_force = datetime.strptime(data['dateEntryIntoForce'], '%Y-%m-%d').date()
    if data['dateIncomingED'] is not None:
        date_incoming_ed = datetime.strptime(data['dateIncomingED'], '%Y-%m-%d').date()
    if data['dateStopCase'] is not None:
        date_stop_case = datetime.strptime(data['dateStopCase'], '%Y-%m-%d').date()

    if data['summaClaim'] is not None:
        summa_claim = round(float(data['summaClaim']) * 100)


    case_id = data['id']
    user_id = data['user_id']

    legal_num = await number_case_legal(data, session)

    legal_data = {"legal_number": legal_num,
                     "legal_section_id": data['legalSection_id'],
                     "number_case_1": data['numberCase_1'],
                     "legal_docs_id": data['legalDocs_id'],
                     "date_session_1": date_session_1,
                     "date_result_1": date_result_1,
                     "result_1_id": data['result_1_id'],
                     "date_entry_force": date_entry_force,
                     "tribunal_1_id": data['tribun_1_id'],
                     "summa_claim": summa_claim,
                     "date_incoming_ed": date_incoming_ed,
                     "date_stop_case": date_stop_case,
                     "comment": data['comment'],
                     "credit_id": data['credit_id'],
                     }

    save_case = await save_case_legal(case_id, user_id, legal_data, session)

    return save_case