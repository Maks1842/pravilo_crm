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



# Получить/добавить КАС
router_appeal = APIRouter(
    prefix="/v1/Appeal",
    tags=["LegalWork"]
)


@router_appeal.get("/")
async def get_appeal(page: int, credit_id: int = None, cession_id: int = None, legal_section_id: int = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):

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
            result_2 = ''
            result_2_id = None
            summa_ed = None
            summa_state_duty_result = None
            summa_state_duty_claim = None
            summa_result_2 = None
            date_session_1 = None
            date_result_1 = None
            date_incoming_ed = None
            date_entry_force = None
            date_cancel_result = None
            date_session_2 = None
            date_result_2 = None
            tribunal_1 = ''
            tribunal_1_id = None
            address_tribunal_1 = ''
            email_tribunal_1 = ''
            phone_tribunal_1 = ''
            tribunal_2 = ''
            tribunal_2_id = None
            address_tribunal_2 = ''
            email_tribunal_2 = ''
            phone_tribunal_2 = ''
            date_court_costs = None
            result_court_costs = None
            result_court_costs_id = None
            date_collection = None
            date_contract = None
            date_ed = None
            gaspravosudie_1 = 'НЕ возможно'
            gaspravosudie_2 = 'НЕ возможно'

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

            if item.result_2_id is not None:
                result_2_id: int = item.result_2_id
                result_2_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == result_2_id))
                result_2 = result_2_query.scalar()

            if item.result_court_costs_id is not None:
                result_court_costs_id: int = item.result_court_costs_id
                result_court_costs_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == result_court_costs_id))
                result_court_costs = result_court_costs_query.scalar()

            if item.summa_ed is not None:
                summa_ed = item.summa_ed / 100
            if item.summa_state_duty_result is not None:
                summa_state_duty_result = item.summa_state_duty_result / 100
            if item.summa_state_duty_claim is not None:
                summa_state_duty_claim = item.summa_state_duty_claim / 100
            if item.summa_result_2 is not None:
                summa_result_2 = item.summa_result_2 / 100

            if item.date_session_1 is not None:
                date_session_1 = datetime.strptime(str(item.date_session_1), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_result_1 is not None:
                date_result_1 = datetime.strptime(str(item.date_result_1), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_incoming_ed is not None:
                date_incoming_ed = datetime.strptime(str(item.date_incoming_ed), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_entry_force is not None:
                date_entry_force = datetime.strptime(str(item.date_entry_force), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_cancel_result is not None:
                date_cancel_result = datetime.strptime(str(item.date_cancel_result), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_session_2 is not None:
                date_session_2 = datetime.strptime(str(item.date_session_2), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_result_2 is not None:
                date_result_2 = datetime.strptime(str(item.date_result_2), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_court_costs is not None:
                date_court_costs = datetime.strptime(str(item.date_court_costs), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_collection is not None:
                date_collection = datetime.strptime(str(item.date_collection), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_contract is not None:
                date_contract = datetime.strptime(str(item.date_contract), '%Y-%m-%d').strftime("%d.%m.%Y")
            if item.date_ed is not None:
                date_ed = datetime.strptime(str(item.date_ed), '%Y-%m-%d').strftime("%d.%m.%Y")

            if item.tribunal_1_id is not None:
                tribunal_1_id: int = item.tribunal_1_id
                tribunal_1_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == tribunal_1_id))
                tribunal_1_set = tribunal_1_query.mappings().one()

                tribunal_1 = tribunal_1_set.name
                address_tribunal_1 = tribunal_1_set.address
                email_tribunal_1 = tribunal_1_set.email
                phone_tribunal_1 = tribunal_1_set.phone
                if tribunal_1_set.gaspravosudie == True:
                    gaspravosudie_1 = 'Возможно'

            if item.tribunal_2_id is not None:
                tribunal_2_id: int = item.tribunal_2_id
                tribunal_2_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == tribunal_2_id))
                tribunal_2_set = tribunal_2_query.mappings().one()

                tribunal_2 = tribunal_2_set.name
                address_tribunal_2 = tribunal_2_set.address
                email_tribunal_2 = tribunal_2_set.email
                phone_tribunal_2 = tribunal_2_set.phone
                if tribunal_2_set.gaspravosudie == True:
                    gaspravosudie_2 = 'Возможно'

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
                "numberCase_2": item.number_case_2,
                "result_2": result_2,
                "result_2_id": result_2_id,
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
                "dateCancelResult": date_cancel_result,
                "dateSession_2": date_session_2,
                "dateResult_2": date_result_2,
                "summaResult_2": summa_result_2,
                "comment": item.comment,
                "tribun_2": tribunal_2,
                "tribun_2_id": tribunal_2_id,
                "addressTribun_2": address_tribunal_2,
                "emailTribun_2": email_tribunal_2,
                "phoneTribun_2": phone_tribunal_2,
                "dateCourtCosts": date_court_costs,
                "resultCourtCosts": result_court_costs,
                "resultCourtCosts_id": result_court_costs_id,
                "dateCollection": date_collection,
                "numberContract": item.comment,
                "dateContract": date_contract,
                "numberED": item.number_ed,
                "dateED": date_ed,
                "gaspravosudie_1": gaspravosudie_1,
                "gaspravosudie_2": gaspravosudie_2,
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


@router_appeal.post("/")
async def add_appeal(data: dict, session: AsyncSession = Depends(get_async_session)):

    if data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }
    date_session_1 = None
    date_result_1 = None
    date_entry_force = None
    date_session_2 = None
    date_result_2 = None
    date_court_costs = None
    date_ed = None
    date_collection = None
    date_contract = None
    summa_ed = None

    if data['dateSession_1'] is not None:
        date_session_1 = datetime.strptime(data['dateSession_1'], '%Y-%m-%d').date()

    if data['dateResult_1'] is not None:
        date_result_1 = datetime.strptime(data['dateResult_1'], '%Y-%m-%d').date()

    if data['dateEntryIntoForce'] is not None:
        date_entry_force = datetime.strptime(data['dateEntryIntoForce'], '%Y-%m-%d').date()

    if data['dateSession_2'] is not None:
        date_session_2 = datetime.strptime(data['dateSession_2'], '%Y-%m-%d').date()

    if data['dateResult_2'] is not None:
        date_result_2 = datetime.strptime(data['dateResult_2'], '%Y-%m-%d').date()

    if data['dateCourtCosts'] is not None:
        date_court_costs = datetime.strptime(data['dateCourtCosts'], '%Y-%m-%d').date()

    if data['dateED'] is not None:
        date_ed = datetime.strptime(data['dateED'], '%Y-%m-%d').date()

    if data['dateCollection'] is not None:
        date_collection = datetime.strptime(data['dateCollection'], '%Y-%m-%d').date()

    if data['dateContract'] is not None:
        date_contract = datetime.strptime(data['dateContract'], '%Y-%m-%d').date()

    if data['summaED'] is not None:
        summa_ed = round(float(data['summaED']) * 100)

    case_id = data['id']

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
                 "comment": data['comment'],
                 "number_case_2": data['numberCase_2'],
                 "date_session_2": date_session_2,
                 "date_result_2": date_result_2,
                 "result_2_id": data['result_2_id'],
                 "tribunal_2_id": data['tribun_2_id'],
                 "date_court_costs": date_court_costs,
                 "result_court_costs_id": data['resultCourtCosts_id'],
                 "number_ed": data['numberED'],
                 "date_ed": date_ed,
                 "summa_ed": summa_ed,
                 "date_collection": date_collection,
                 "number_contract": data['numberContract'],
                 "date_contract": date_contract,
                 "credit_id": data['credit_id'],
                     }

    save_case = await save_case_legal(case_id, legal_data, session)

    return save_case