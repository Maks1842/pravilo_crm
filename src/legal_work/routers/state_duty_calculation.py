from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor
from src.legal_work.routers.helper_legal_work import number_case_legal, save_case_legal


# Рассчитать сумму госпошлины
router_duty_legal_calculation = APIRouter(
    prefix="/v1/StateDutyLegalCalculation",
    tags=["LegalWork"]
)


@router_duty_legal_calculation.post("/")
async def add_tribunal_write(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']

    credit_not_save = []
    count = 0
    count_error = 0
    for credit_id in data['list_credit_id']:
        summa_state_duty_claim = 0

        credit_query = await session.execute(select(credit).where(credit.c.id == int(credit_id)))
        credit_set = credit_query.mappings().fetchone()
        debtor_id: int = credit_set.debtor_id

        if data['legalSection_name'] == 'СП':
            summa_state_duty_claim = duty_tribunal_write_calculate(credit_set)

        debtor_query = await session.execute(select(debtor.c.tribunal_id).where(debtor.c.id == debtor_id))
        tribunal_id: int = debtor_query.scalar()

        if summa_state_duty_claim:
            case_id = data['id']

            legal_num = await number_case_legal(data, session)

            legal_data = {"legal_number": legal_num,
                             "legal_section_id": data['legalSection_id'],
                             "legal_docs_id": data['legalDocs_id'],
                             "tribunal_1_id": tribunal_id,
                             "summa_state_duty_claim": summa_state_duty_claim,
                             "credit_id": credit_id,
                             }

            await save_case_legal(case_id, legal_data, session)
            count += 1
        else:
            credit_not_save.append(credit_set.number)
            count_error += 1

    return {
        'status': 'success',
        'data': None,
        'details': f'Расчитана и записана Госпошлина по {count} кредитам. Не расчитана Госпошлина по {count_error} кредитам, {credit_not_save}'
    }


def duty_tribunal_write_calculate(credit_set):

    summa_claim = 0
    state_duty = None

    if credit_set.summa_by_cession is not None:
        summa_by_cession = credit_set.summa_by_cession

        if summa_by_cession <= 2000000:
            summa_claim = summa_by_cession * 0.04
            if summa_claim < 40000:
                summa_claim = 40000
        elif summa_by_cession > 2000000 and summa_by_cession <= 10000000:
            difference = summa_by_cession - 2000000
            summa_claim = 80000 + difference * 0.03
        elif summa_by_cession > 10000000 and summa_by_cession <= 20000000:
            difference = summa_by_cession - 10000000
            summa_claim = 320000 + difference * 0.02
        elif summa_by_cession > 20000000 and summa_by_cession <= 100000000:
            difference = summa_by_cession - 20000000
            summa_claim = 520000 + difference * 0.01
        elif summa_by_cession > 100000000:
            difference = summa_by_cession - 100000000
            summa_claim = 1320000 + difference * 0.005
            if summa_claim > 6000000:
                summa_claim = 6000000

        state_duty = round(summa_claim / 2)

    return state_duty