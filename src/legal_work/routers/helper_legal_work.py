from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.legal_work.models import legal_work
from src.debts.models import credit
from src.tasks.models import task
from variables_for_backend import VarStatusCD, VarSectionCard
from src.debts.router import func_save_credit
from src.tasks.router import func_save_task

from datetime import date


# Получить уникальные номера судебных кейсов
router_get_legal_number = APIRouter(
    prefix="/v1/GetLegalNumbers",
    tags=["LegalWork"]
)


@router_get_legal_number.get("/")
async def get_legal_number(credit_id: int = None, legal_section_id: int = None, session: AsyncSession = Depends(get_async_session)):

    result = []
    if credit_id:
        legal_query = await session.execute(select(legal_work.c.id, legal_work.c.legal_number).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id == credit_id)))

        for item in legal_query.mappings().all():
            result.append({"legal_id": item.id, "legal_number": item.legal_number})
    else:
        legal_query = await session.execute(select(legal_work.c.id, legal_work.c.legal_number).where(and_(legal_work.c.legal_section_id == legal_section_id, legal_work.c.credit_id == credit_id)))

        for item in legal_query.mappings().all():
            result.append({"legal_id": item.id, "legal_number": item.legal_number})

    return result


async def number_case_legal(data, session):
    legal_section = str(data['legalSection_id']).zfill(2)
    legal_num = data['legalNumber']
    if data['legalNumber'] is None:
        try:
            legal_section_id: int = data['legalSection_id']
            legal_work_query = await session.execute(select(legal_work).where(legal_work.c.legal_section_id == legal_section_id).order_by(desc(legal_work.c.id)))
            legal_work_set = legal_work_query.mappings().fetchone()

            if len(legal_work_set['legal_number']) > 0:
                legal_number_split = legal_work_set['legal_number'][3:]
                legal_number_body = str(int(legal_number_split) + 1).zfill(7)
                legal_num = f'{legal_section}/{legal_number_body}'
        except:
            legal_num = f'{legal_section}/0000001'

    return legal_num


async def save_case_legal(case_id, user_id, legal_data, session):

    credit_id: int = legal_data['credit_id']
    legal_work_query = await session.execute(select(legal_work.c.id).where(legal_work.c.credit_id == credit_id))
    legal_work_set = legal_work_query.mappings().all()

    if len(legal_work_set) == 0:
        credit_query = await session.execute(select(credit.c.status_cd_id).where(credit.c.id == credit_id))
        status_cd_id = credit_query.scalar()

        if status_cd_id == VarStatusCD.status_cd_none:
            data_cd = {"status_cd_id": VarStatusCD.status_cd_rab}
            await func_save_credit(credit_id, data_cd, session)

    try:
        if case_id:
            post_data = update(legal_work).where(legal_work.c.id == int(case_id)).values(legal_data)
        else:
            post_data = insert(legal_work).values(legal_data)

        await session.execute(post_data)
        await session.commit()
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении судебного кейса. {ex}"
        }

    task_query = await session.execute(select(task.c.id).where(and_(task.c.user_id == user_id,
                                                                    task.c.section_card_debtor_id == VarSectionCard.section_card_id_tribun,
                                                                    task.c.credit_id == credit_id,
                                                                    task.c.name_id == int(legal_data['legal_docs_id']),
                                                                    task.c.date_statement.is_(None),
                                                                    task.c.date_answer.is_(None))))
    task_list = task_query.mappings().all()
    if case_id is None and len(task_list) == 0:

        task_id = None
        try:
            task_data = {
                  "name_id": legal_data['legal_docs_id'],
                  "section_card_debtor_id": VarSectionCard.section_card_id_tribun,
                  "type_statement_id": None,
                  "date_task": date.today(),
                  "timeframe": None,
                  "user_id": int(user_id),
                  "date_statement": None,
                  "track_num": '',
                  "date_answer": None,
                  "result_id": None,
                  "credit_id": credit_id,
                  "comment": None}

            await func_save_task(task_id, task_data, session)
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f"Судебный кейс успешно сохранен. Ошибка при добавлении задачи. {ex}"
            }
    return {
        'status': 'success',
        'data': None,
        'details': 'Судебный кейс успешно сохранен'
    }