import math
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.legal_work.models import legal_work
from src.legal_work.routers.helper_legal_work import number_case_legal, save_case_legal
from src.references.models import ref_legal_docs, ref_result_statement, ref_tribunal

'''
Метод для судебной работы
'''



# Получить/добавить Иск
router_claim = APIRouter(
    prefix="/v1/Claim",
    tags=["LegalWork"]
)


@router_claim.get("/")
async def get_claim(page: int, credit_id: int = None, cession_id: int = None, legal_section_id: int = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20

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
            summa_ed = None
            summa_claim = None
            summa_state_duty_result = None
            summa_state_duty_claim = None
            date_session_1 = None
            date_result_1 = None
            date_incoming_ed = None
            date_entry_force = None
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
            if item.summa_ed is not None:
                summa_ed = item.summa_ed / 100
            if item.summa_state_duty_result is not None:
                summa_state_duty_result = item.summa_state_duty_result / 100
            if item.summa_state_duty_claim is not None:
                summa_state_duty_claim = item.summa_state_duty_claim / 100

            if item.date_session_1 is not None:
                date_session_1 = datetime.strptime(str(item.date_session_1), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_result_1 is not None:
                date_result_1 = datetime.strptime(str(item.date_result_1), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_incoming_ed is not None:
                date_incoming_ed = datetime.strptime(str(item.date_incoming_ed), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_entry_force is not None:
                date_entry_force = datetime.strptime(str(item.date_entry_force), '%Y-%m-%d').strftime("%d.%m.%Y")

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
                "summaED": summa_ed,
                "summaStateDutyClaim": summa_state_duty_claim,
                "summaStateDutyResult": summa_state_duty_result,
                "dateIncomingED": date_incoming_ed,
                "dateEntryIntoForce": date_entry_force,
                "tribun_1": tribunal_1,
                "tribun_1_id": tribunal_1_id,
                "addressTribun_1": address_tribunal_1,
                "emailTribun_1": email_tribunal_1,
                "phoneTribun_1": phone_tribunal_1,
                "comment": item.comment,
                "tribun_2_id": None,
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


@router_claim.post("/")
async def add_claim(data: dict, session: AsyncSession = Depends(get_async_session)):

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
    summa_claim = None
    summa_ed = None
    summa_state_duty_claim = None
    summa_state_duty_result = None

    if data['dateSession_1'] is not None:
        date_session_1 = datetime.strptime(data['dateSession_1'], '%Y-%m-%d').date()

    if data['dateResult_1'] is not None:
        date_result_1 = datetime.strptime(data['dateResult_1'], '%Y-%m-%d').date()

    if data['dateEntryIntoForce'] is not None:
        date_entry_force = datetime.strptime(data['dateEntryIntoForce'], '%Y-%m-%d').date()

    if data['dateIncomingED'] is not None:
        date_incoming_ed = datetime.strptime(data['dateIncomingED'], '%Y-%m-%d').date()

    if data['summaClaim'] is not None:
        summa_claim = round(float(data['summaClaim']) * 100)

    if data['summaED'] is not None:
        summa_ed = round(float(data['summaED']) * 100)

    if data['summaStateDutyClaim'] is not None:
        summa_state_duty_claim = round(float(data['summaStateDutyClaim']) * 100)

    if data['summaStateDutyResult'] is not None:
        summa_state_duty_result = round(float(data['summaStateDutyResult']) * 100)


    case_id = data['id']

    legal_num = await number_case_legal(data, session)

    legal_data = {"legal_number": legal_num,
                     "legal_section_id": data['legalSection_id'],
                     "number_case_1": data['numberCase_1'],
                     "legal_docs_id": data['legalDocs_id'],
                     "date_session_1": date_session_1,
                     "date_result_1": date_result_1,
                     "result_1_id": data['result_1_id'],
                     "summa_claim": summa_claim,
                     "summa_ed": summa_ed,
                     "summa_state_duty_claim": summa_state_duty_claim,
                     "summa_state_duty_result": summa_state_duty_result,
                     "date_incoming_ed": date_incoming_ed,
                     "date_entry_force": date_entry_force,
                     "tribunal_1_id": data['tribun_1_id'],
                     "comment": data['comment'],
                     "credit_id": data['credit_id'],
                     }

    save_case = await save_case_legal(case_id, legal_data, session)

    return save_case