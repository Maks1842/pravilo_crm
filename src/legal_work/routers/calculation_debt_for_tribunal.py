from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor, cession
from src.routers_helper.data_to_excel.calculating_debt_excel import calculating_debt_to_excel, calculating_annuity_to_excel
from src.routers_helper.rout_calculator.calculation_annuity_payment import get_calculation_annuity


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
        overdue_od = 0

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
        if credit_set.overdue_od is not None:
            overdue_od = credit_set.overdue_od / 100

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
                'overdue_od': overdue_od,
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


# Рассчитать аннуитетные платежи
router_calculation_annuity_payment = APIRouter(
    prefix="/v1/CalculationAnnuityPayment",
    tags=["LegalWork"]
)


@router_calculation_annuity_payment.post("/")
async def calculation_annuity_payment(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']

    credit_id: int = data['credit_id']
    date_start_pay = data['date_start_pay']
    date_end_pay = data['date_end_pay']
    period = data['period']
    summa_payments = data['summa_payments']
    summa_pay_start = data['summa_pay_start']
    summa_percent_start = data['summa_percent_start']
    timeline = data['timeline']

    summa = 0
    overdue_od = 0

    credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
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
    if credit_set.overdue_od is not None:
        overdue_od = credit_set.overdue_od / 100

    if credit_set.date_start is None:
        return {
            "status": "error",
            "data": None,
            "details": f'Отсутствует дата выдачи КД {credit_set.number}'
        }

    data_func = {
            "date_start_cd": credit_set.date_start,
            "summa_cd": summa,
            "interest_rate": credit_set.interest_rate,
            'date_start_pay': date_start_pay,
            'date_end_pay': date_end_pay,
            'period': period,
            'summa_payments': summa_payments,
            'summa_pay_start': summa_pay_start,
            'summa_percent_start': summa_percent_start,
            'overdue_od': overdue_od,
            'timeline': timeline
            }

    result = get_calculation_annuity(data_func)

    data_to_exl = {
        "fio": fio,
        "number_cd": credit_set.number,
        "date_start_cd": credit_set.date_start,
        "summa_cd": summa,
        'overdue_od': overdue_od,
        "interest_rate": credit_set.interest_rate,
        "date_end": credit_set.date_end,
        "cession_date": cession_date,
        "result": result['annuity_list'],
        "summ_percent_total": result['summ_percent_total']
    }

    result_calculator = calculating_annuity_to_excel(data_to_exl)

    return result_calculator