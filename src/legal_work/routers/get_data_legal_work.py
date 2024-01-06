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


# Получить данные о судебке по id
router_data_legal = APIRouter(
    prefix="/v1/GetDataLegal",
    tags=["LegalWork"]
)


@router_data_legal.get("/")
async def get_data_legal(legal_id: int, session: AsyncSession = Depends(get_async_session)):

    try:
        legal_query = await session.execute(select(legal_work).where(legal_work.c.id == legal_id))
        item = legal_query.fetchone()

        credit_id: int = item.credit_id

        legal_docs = ''
        legal_docs_id = None
        legal_date = None
        result_1 = ''
        result_1_id = None
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
        gaspravosudie = 'НЕ возможно'

        credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
        credit_set = credit_query.mappings().one()
        cession_id: int = credit_set.cession_id

        cession_query = await session.execute(select(cession).where(cession.c.id == cession_id))
        cession_set = cession_query.mappings().one()

        debtor_id: int = credit_set.debtor_id

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
        debtor_item = debtor_query.mappings().one()

        # if debtor_item.last_name_2:
        #     debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
        #                  f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
        # else:
        #     debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

        if item.legal_docs_id:
            name_task_query = await session.execute(select(ref_legal_docs.c.name).where(ref_legal_docs.c.id == int(item.legal_docs_id)))
            legal_docs = name_task_query.scalar()
            legal_docs_id = item.legal_docs_id

        if item.result_1_id:
            result_1_id: int = item.result_1_id
            result_1_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == result_1_id))
            result_1 = result_1_query.scalar()

        # if item.summa_ed:
        #     summa_ed = item.summa_ed / 100
        # if item.summa_state_duty_result:
        #     summa_state_duty_result = item.summa_state_duty_result / 100
        # if item.summa_state_duty_claim:
        #     summa_state_duty_claim = item.summa_state_duty_claim / 100
        # if item.summa_result_2:
        #     summa_result_2 = item.summa_result_2 / 100

        if item.date_session_1:
            date_session_1 = datetime.strptime(str(item.date_session_1), '%Y-%m-%d').strftime("%d.%m.%Y")
        # if item.date_result_1:
        #     date_result_1 = datetime.strptime(str(item.date_result_1), '%Y-%m-%d').strftime("%d.%m.%Y")
        # if item.date_incoming_ed:
        #     date_incoming_ed = datetime.strptime(str(item.date_incoming_ed), '%Y-%m-%d').strftime("%d.%m.%Y")
        # if item.date_entry_force:
        #     date_entry_force = datetime.strptime(str(item.date_entry_force), '%Y-%m-%d').strftime("%d.%m.%Y")
        # if item.date_cancel_result:
        #     date_cancel_result = datetime.strptime(str(item.date_cancel_result), '%Y-%m-%d').strftime("%d.%m.%Y")
        # if item.date_session_2:
        #     date_session_2 = datetime.strptime(str(item.date_session_2), '%Y-%m-%d').strftime("%d.%m.%Y")
        # if item.date_result_2:
        #     date_result_2 = datetime.strptime(str(item.date_result_2), '%Y-%m-%d').strftime("%d.%m.%Y")
        if item.legal_date:
            legal_date = datetime.strptime(str(item.legal_date), '%Y-%m-%d').strftime("%d.%m.%Y")

        if item.tribunal_1_id:
            tribunal_1_id: int = item.tribunal_1_id
            # tribunal_1_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == tribunal_1_id))
            # tribunal_1_set = tribunal_1_query.mappings().one()
            #
            # tribunal_1 = tribunal_1_set.name
            # address_tribunal_1 = tribunal_1_set.address
            # email_tribunal_1 = tribunal_1_set.email
            # phone_tribunal_1 = tribunal_1_set.phone
            # if tribunal_1_set.gaspravosudie == True:
            #     gaspravosudie = 'Возможно'

        result = {
            "id": item.id,
            "legalNumber": item.legal_number,
            "dateLegal": legal_date,
            "legalSection_id": item.legal_section_id,
            "credit_id": item.credit_id,
            # "credit": credit_set.number,
            "cession_id": cession_set.id,
            # "cessionName": cession_set.name,
            # "debtorName": debtor_fio,
            # "numberCase_1": item.number_case_1,
            # "legalDocs": legal_docs,
            "legalDocs_id": legal_docs_id,
            "dateSession_1": date_session_1,
            # "dateResult_1": date_result_1,
            # "result_1": result_1,
            "result_1_id": result_1_id,
            # "summaED": summa_ed,
            # "summaStateDutyClaim": summa_state_duty_claim,
            # "summaStateDutyResult": summa_state_duty_result,
            # "dateIncomingED": date_incoming_ed,
            # "dateEntryIntoForce": date_entry_force,
            # "tribun_1": tribunal_1,
            "tribun_1_id": tribunal_1_id,
            # "addressTribun_1": address_tribunal_1,
            # "emailTribun_1": email_tribunal_1,
            # "phoneTribun_1": phone_tribunal_1,
            # "dateCancelResult": date_cancel_result,
            # "dateSession_2": date_session_2,
            # "dateResult_2": date_result_2,
            # "summaResult_2": summa_result_2,
            # "comment": item.comment,
            "tribun_2_id": None,
            # "gaspravosudie": gaspravosudie,
        }

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }