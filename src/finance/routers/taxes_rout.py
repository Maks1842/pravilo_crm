from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit
from src.payments.models import payment
from src.finance.models import expenses
from src.finance.routers.expenses_rout import save_expenses

from datetime import datetime



# Рассчитать налоги и агентские
router_calculator_taxes = APIRouter(
    prefix="/v1/CalculatorTax",
    tags=["Finance"]
)


@router_calculator_taxes.post("/")
async def get_calculator_taxes(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    summa = 0
    taxes_percent = 6
    summa_taxes = 0
    summa_agency = 0

    month: int = data_json['month']['text']
    month_id: int = data_json['month']['value']
    year: int = data_json['year']
    cession_id: int = data_json['cession_id']
    agency_percent: int = data_json['agencyFee']

    credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
    credits_id_list = credits_id_query.scalars().all()

    if len(credits_id_list) > 0:
        summa_query = await session.execute(select(func.sum(payment.c.summa)).filter(and_(extract('month', payment.c.date) == month_id,
                                                                                          extract('year', payment.c.date) == year,
                                                                                          payment.c.credit_id.in_(credits_id_list))))
        summa = summa_query.scalar()

    if data_json['checkboxTax'] and summa:
        summa_taxes = round(summa * taxes_percent / 100 / 100, 2)

    if data_json['checkboxAgent'] and summa:
        summa_agency = round(summa * float(agency_percent) / 100 / 100, 2)

    result = {'summaTax': summa_taxes, 'summaAgent': summa_agency, 'cession_id': cession_id, 'month': month, 'month_id': month_id, 'year': year, 'agency_percent': agency_percent}

    return result


# Сохранить налоги и агентские
router_save_taxes = APIRouter(
    prefix="/v1/SaveTaxes",
    tags=["Finance"]
)

@router_save_taxes.post("/")
async def add_taxes(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    reg_data = data_json['data_json']
    result = {
        "status": "error",
        "data": None,
        "details": f"Отсутствуют данные для добавления в Расходы"
    }

    try:
        if reg_data["month_id"] < 10:
            date_join = f'{reg_data["year"]}-0{reg_data["month_id"]}-28'
        else:
            date_join = f'{reg_data["year"]}-{reg_data["month_id"]}-28'

        date_tax = datetime.strptime(str(date_join), '%Y-%m-%d').date()

        if reg_data['summaTax'] > 0:
            expenses_tax_query = await session.execute(select(expenses.c.id).where(and_(expenses.c.expenses_category_id == 7,
                                                                                        expenses.c.date == date_tax)))
            expenses_tax_item = expenses_tax_query.mappings().fetchone()
            if expenses_tax_item:
                return {
                    "status": "error",
                    "data": None,
                    "details": f'Подоходный налог за {reg_data["month"]} {reg_data["year"]} г. уже существует'
                }
            else:
                data = {
                        "id": None,
                        "date": date_join,
                        "summa": reg_data['summaTax'],
                        "expenses_category_id": 7,
                        "payment_purpose": f'Подоходный налог за {reg_data["month"]} {reg_data["year"]} г.',
                        "cession_id": reg_data['cession_id'],
                        }
                result = await save_expenses(data, session)

        if reg_data['summaAgent'] > 0:
            expenses_agent_query = await session.execute(select(expenses.c.id).where(and_(expenses.c.expenses_category_id == 8,
                                                                                          expenses.c.date == date_tax)))
            expenses_agent_item = expenses_agent_query.mappings().fetchone()

            if expenses_agent_item:
                return {
                    "status": "error",
                    "data": None,
                    "details": f'Агентское вознаграждение {reg_data["agency_percent"]}% за {reg_data["month"]} {reg_data["year"]} г. уже существует'
                }
            else:
                data = {
                    "id": None,
                    "date": date_join,
                    "summa": reg_data['summaAgent'],
                    "expenses_category_id": 8,
                    "payment_purpose": f'Агентское вознаграждение {reg_data["agency_percent"]}% за {reg_data["month"]} {reg_data["year"]} г.',
                    "cession_id": reg_data['cession_id'],
                }

                result = await save_expenses(data, session)
    except Exception as ex:
        result = {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }

    return result