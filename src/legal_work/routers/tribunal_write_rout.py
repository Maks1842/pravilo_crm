import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.tasks.models import task
from src.legal_work.models import legal_work
from src.legal_work.routers.helper_legal_work import number_case_legal, save_case_legal
from src.references.models import ref_task, ref_result_statement, ref_tribunal

'''
Метод для судебной работы
'''



# Получить/добавить СП
router_tribunal_write = APIRouter(
    prefix="/v1/TribunalWrite",
    tags=["LegalWork"]
)


@router_tribunal_write.get("/")
async def get_tribunal_write(page: int, credit_id: int = None, cession_id: int = None, legal_section_id: int = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20

    if dates2 is None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    try:
        if credit_id == None and dates1:
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.date_session_1 >= dates1, legal_work.c.date_session_1 <= dates2)).
                                               order_by(desc(legal_work.c.legal_number)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.date_session_1 == dates1))))
        elif credit_id and dates1 == None:
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id == credit_id)).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id == credit_id))))
        elif cession_id and dates1 == None:
            credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
            credits_id_list = credits_id_query.scalars().all()
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list))).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list)))))
        elif cession_id and dates1:
            credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
            credits_id_list = credits_id_query.scalars().all()
            legal_query = await session.execute(select(legal_work).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list), legal_work.c.date_session_1 >= dates1, legal_work.c.date_session_1 <= dates2)).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id.in_(credits_id_list), legal_work.c.date_session_1 >= dates1, legal_work.c.date_session_1 <= dates2))))
        else:
            legal_query = await session.execute(select(legal_work).where(legal_work.c.legal_section_id == legal_section_id).
                                                order_by(desc(legal_work.c.legal_number)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(legal_work.c.legal_section_id == legal_section_id)))

        total_item = total_item_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_legal = []
        for item in legal_query.mappings().all():

            credit_id: int = item['credit_id']

            name_task = ''
            name_task_id = ''
            result_1 = ''
            result_1_id = ''
            tribunal_1 = ''
            tribunal_1_id = ''
            address_tribunal_1 = ''
            email_tribunal_1 = ''
            phone_tribunal_1 = ''
            gaspravosudie = 'НЕ возможно'

            credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
            credit_set = credit_query.mappings().one()
            cession_id: int = credit_set['cession_id']

            cession_query = await session.execute(select(cession).where(cession.c.id == cession_id))
            cession_set = cession_query.mappings().one()

            debtor_id: int = credit_set['debtor_id']

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()

            if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
                debtor_fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                             f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
            else:
                debtor_fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

            if item['name_task_id'] is not None and item['name_task_id'] != '':
                name_task_query = await session.execute(select(ref_task.c.name).where(ref_task.c.id == int(item['name_task_id'])))
                name_task = name_task_query.scalar()
                name_task_id = item['name_task_id']

            if item['result_1_id'] is not None and item['result_1_id'] != '':
                result_1_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == int(item['result_1_id'])))
                result_1 = result_1_query.scalar()
                result_1_id = item['result_1_id']

            if item['tribunal_1_id'] is not None and item['tribunal_1_id'] != '':
                tribunal_1_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == int(item['tribunal_1_id'])))
                tribunal_1_set = tribunal_1_query.mappings().one()
                tribunal_1_id = item['tribunal_1_id']
                tribunal_1 = tribunal_1_set['name']
                address_tribunal_1 = tribunal_1_set['address']
                email_tribunal_1 = tribunal_1_set['email']
                phone_tribunal_1 = tribunal_1_set['phone']
                if tribunal_1_set['gaspravosudie'] == True:
                    gaspravosudie = 'Возможно'

            data_legal.append({
                "id": item['id'],
                "legalNumber": item['legal_number'],
                "legalSection_id": item['legal_section_id'],
                "credit_id": item['credit_id'],
                "credit": credit_set['number'],
                "cession_id": cession_set['id'],
                "cessionName": cession_set['name'],
                "debtorName": debtor_fio,
                "numberCase_1": item['number_case_1'],
                "nameTask": name_task,
                "nameTask_id": name_task_id,
                "dateSession_1": item['date_session_1'],
                "dateResult_1": item['date_result_1'],
                "result_1": result_1,
                "result_1_id": result_1_id,
                "summaED": item['summa_ed'],
                "summaStateDutyResult": item['summa_state_duty_result'],
                "dateIncomingED": item['date_incoming_ed'],
                "dateEntryIntoForce": item['date_entry_force'],
                "tribun_1": tribunal_1,
                "tribun_1_id": tribunal_1_id,
                "addressTribun_1": address_tribunal_1,
                "emailTribun_1": email_tribunal_1,
                "phoneTribun_1": phone_tribunal_1,
                "dateCancelResult": item['date_cancel_result'],
                "dateSession_2": item['date_session_2'],
                "dateResult_2": item['date_result_2'],
                "summaResult_2": item['summa_result_2'],
                "comment": item['comment'],
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


@router_tribunal_write.post("/")
async def add_tribunal_write(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']


    if data['credit_id'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не выбран Должник и № Кредитного договора"
        }
    date_result_1 = None
    date_entry_force = None
    date_incoming_ed = None
    date_cancel_result = None
    date_session_2 = None
    date_result_2 = None
    summa_ed = None
    summa_state_duty_result = None
    summa_result_2 = None

    if data['dateResult_1'] is not None:
        date_result_1 = datetime.strptime(data['dateResult_1'], '%Y-%m-%d').date()

    if data['dateEntryIntoForce'] is not None:
        date_entry_force = datetime.strptime(data['dateEntryIntoForce'], '%Y-%m-%d').date()

    if data['dateIncomingED'] is not None:
        date_incoming_ed = datetime.strptime(data['dateIncomingED'], '%Y-%m-%d').date()

    if data['dateCancelResult'] is not None:
        date_cancel_result = datetime.strptime(data['dateCancelResult'], '%Y-%m-%d').date()

    if data['dateSession_2'] is not None:
        date_session_2 = datetime.strptime(data['dateSession_2'], '%Y-%m-%d').date()

    if data['dateResult_2'] is not None:
        date_result_2 = datetime.strptime(data['dateResult_2'], '%Y-%m-%d').date()

    if data['summaED'] is not None:
        summa_ed = int(float(data['summaED'])) * 100

    if data['summaStateDutyResult'] is not None:
        summa_state_duty_result = int(float(data['summaStateDutyResult'])) * 100

    if data['summaResult_2'] is not None:
        summa_result_2 = int(float(data['summaResult_2'])) * 100


    case_id = data['id']

    legal_num = await number_case_legal(data, session)

    legal_data = {"legal_number": legal_num,
                     "legal_section_id": data['legalSection_id'],
                     "number_case_1": data['numberCase_1'],
                     "name_task_id": data['nameTask_id'],
                     # "date_session_1": datetime.strptime(data['dateSession_1'], '%Y-%m-%d').date(),
                     "date_result_1": date_result_1,
                     "result_1_id": data['result_1_id'],
                     "date_entry_force": date_entry_force,
                     "tribunal_1_id": data['tribun_1_id'],
                     "summa_ed": summa_ed,
                     "summa_state_duty_result": summa_state_duty_result,
                     "date_incoming_ed": date_incoming_ed,
                     "date_cancel_result": date_cancel_result,
                     "date_session_2": date_session_2,
                     "date_result_2": date_result_2,
                     "summa_result_2": summa_result_2,
                     "comment": data['comment'],
                     "credit_id": data['credit_id'],
                     }

    save_case = await save_case_legal(case_id, legal_data, session)

    return save_case