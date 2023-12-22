import random
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.start_srm.models import date_start_functions
import src.start_srm.routers.start_functions as start_functions

from variables_for_front import welcome_list
from variables_for_front import VariablesFront


# Роутер для приветствия
router_welcome = APIRouter(
    prefix="/v1/GetWelcomeText",
    tags=["StartCRM"]
)

@router_welcome.get("/")
async def get_welcome_text():

    result = random.choice(welcome_list)

    return result


# Роутер для экспортирования переменных на Фронт
router_export_variables = APIRouter(
    prefix="/v1/GetExportVariables",
    tags=["StartCRM"]
)

@router_export_variables.get("/")
async def export_variables():

    return VariablesFront.variables


# Роутер для Стартовых функций
router_start_functions = APIRouter(
    prefix="/v1/StartFunctions",
    tags=["StartCRM"]
)

@router_start_functions.get("/")
async def start_functions_crm(session: AsyncSession = Depends(get_async_session)):

    current_date = date.today()

    date_start_query = await session.execute(select(date_start_functions).where(date_start_functions.c.number_days == 1))
    date_start_set = date_start_query.mappings().first()

    date_start = date_start_set.date

    if date_start < current_date:
        try:
            data = {'date': current_date}
            post_data = update(date_start_functions).where(date_start_functions.c.id == int(date_start_set.id)).values(data)
            await session.execute(post_data)
            await session.commit()
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f"Стартовые функции НЕ выполнены. Ошибка при добавлении/изменении даты старта функций. {ex}"
            }

        functions = ['control_payment_schedule']

        for f in functions:
            function_start = getattr(start_functions, f)
            await function_start(session)
        result = 'Стартовые функции успешно выполнены'
    else:
        result = 'Повтор. Стартовые функции сегодня уже выполнялись'

    return {
        'status': 'success',
        'data': None,
        'details': result
    }


