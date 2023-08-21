from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import debtor


router_calculating_pensioner = APIRouter(
    prefix="/v1/CalculatingPensioner",
    tags=["Debts"]
)


# Рассчитать признак "Пенсионер" у всех должников
@router_calculating_pensioner.get("/")
async def get_calculating_pensioner(session: AsyncSession = Depends(get_async_session)):

    debtors_query = await session.execute(select(debtor))

    current_date = date.today()

    for item in debtors_query.all():

        debtor_item = dict(item._mapping)

        if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
            fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                  f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
        else:
            fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"
        pensioner = False

        try:
            birthday = debtor_item['birthday']
            period = round((current_date - birthday).days / 365, 2)
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f'Отсутствует дата рождения у {fio}. {ex}'
            }

        try:
            if debtor_item['pol'] == 'м' or debtor_item['pol'] == 'Муж':
                if current_date.year == 2023 and period >= 61.5:
                    pensioner = True
                elif (current_date.year == 2024 or current_date.year == 2025) and period >= 63:
                    pensioner = True
                elif (current_date.year == 2026 or current_date.year == 2027) and period >= 64:
                    pensioner = True
                elif current_date.year >= 2028 and period >= 65:
                    pensioner = True
            elif debtor_item['pol'] == 'ж' or debtor_item['pol'] == 'Жен':
                if current_date.year == 2023 and period >= 56.5:
                    pensioner = True
                elif (current_date.year == 2024 or current_date.year == 2025) and period >= 58:
                    pensioner = True
                elif (current_date.year == 2026 or current_date.year == 2027) and period >= 59:
                    pensioner = True
                elif current_date.year >= 2028 and period >= 60:
                    pensioner = True
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f'Не указан пол у {fio}. {ex}'
            }

        try:
            debtor_id = int(debtor_item["id"])
            data = {
                "pensioner": pensioner,
            }
            post_data = update(debtor).where(debtor.c.id == debtor_id).values(data)

            await session.execute(post_data)
            await session.commit()

        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f"Ошибка определения признака 'Пенсионер'. {ex}"
            }

    return {
        'status': 'success',
        'data': None,
        'details': 'Признак "Пенсионер" успешно рассчитан'
    }