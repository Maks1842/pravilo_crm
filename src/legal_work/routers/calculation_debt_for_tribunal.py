from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor, cession
from src.routers_helper.data_to_excel.calculating_debt_excel import calculating_debt_to_excel


# Рассчитать сумму задолженности по графику
router_calculation_debt = APIRouter(
    prefix="/v1/CalculationDebtForTribunal",
    tags=["LegalWork"]
)


@router_calculation_debt.post("/")
async def calculation_debt(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    list_credit_id = data_json['data_json']

    count = 0
    for credit_id in list_credit_id:
        summa = 0

        credit_query = await session.execute(select(credit).where(credit.c.id == int(credit_id)))
        credit_set = credit_query.mappings().fetchone()
        debtor_id: int = credit_set.debtor_id
        cession_id: int = credit_set.cession_id

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
        debtor_item = debtor_query.mappings().one()

        cession_query = await session.execute(select(cession.c.date).where(cession.c.id == cession_id))
        cession_date = cession_query.scalar()

        if debtor_item.last_name_2 is not None and debtor_item.last_name_2 != '':
            fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                  f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
        else:
            fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

        if credit_set.summa is not None:
            summa = credit_set.summa / 100
        if credit_set.summa is not None:
            summa = credit_set.summa / 100

        if credit_set.date_start is None:
            return {
                "status": "error",
                "data": None,
                "details": f'Отсутствует дата выдачи КД {credit_set.number}'
            }

        data = {"fio": fio,
                "number_cd": credit_set.number,
                "date_start_cd": credit_set.date_start,
                "summa_cd": summa,
                "interest_rate": credit_set.interest_rate,
                "date_end": credit_set.date_end,
                "cession_date": cession_date,
                }

        calculating_debt_to_excel(data)
        count += 1

    return {
        'status': 'success',
        'data': None,
        'details': f'Расчет задолженности произведен по {count} кредитам.'
    }