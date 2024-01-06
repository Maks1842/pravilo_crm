from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit
from src.legal_work.routers.helper_legal_work import number_case_legal, save_case_legal

from datetime import date



# Добавить Судебку из Общего реестра
router_reg_legal_work = APIRouter(
    prefix="/v1/GeneratorLegalWorkList",
    tags=["Registries"]
)


@router_reg_legal_work.post("/")
async def save_legal_work_list(data_dict: dict, session: AsyncSession = Depends(get_async_session)):

    credits_id_array = data_dict['credits_id_array']
    user_id = data_dict['user_id']
    legal_section_id = data_dict['legal_section_id']
    legal_docs_id = data_dict['legal_docs_id']
    case_id = None

    credits_query = await session.execute(select(credit).where(credit.c.id.in_(credits_id_array)))

    for item in credits_query.mappings().all():
        credit_id: int = item.id
        credit_number = item.number

        data_legal_num = {
            "legalNumber": None,
            "legalSection_id": legal_section_id
        }

        try:
            legal_num = await number_case_legal(data_legal_num, session)

            legal_data = {"legal_number": legal_num,
                          "legal_section_id": legal_section_id,
                          "legal_date": date.today(),
                          "legal_docs_id": legal_docs_id,
                          "credit_id": credit_id,
                          }

            await save_case_legal(case_id, user_id, legal_data, session)
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f"Ошибка при сохранении судебного кейса для КД {credit_number}. {ex}"
            }

    return {
        'status': 'success',
        'data': None,
        'details': 'Судебные кейсы успешно сохранены'
    }