from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit
from src.routers_helper.rout_creating_docs.insert_into_txt import paymant_order_txt

'''
Метод формирования документов в формате .txt
Метод принимает список credit_id по которым необходимо сформировать документы
'''


# Сформировать документ .txt
router_generator_txt = APIRouter(
    prefix="/v1/GeneratorTxt",
    tags=["GeneratorDocs"]
)


@router_generator_txt.post("/")
async def generator_txt(data_dict: dict, session: AsyncSession = Depends(get_async_session)):

    try:
        credits_id_array = data_dict['credits_id_array']
        date_order = data_dict['date_order']
        number_order = data_dict['number_order']

        credits_query = await session.execute(select(credit).where(credit.c.id.in_(credits_id_array)))
        credits_list = credits_query.mappings().all()

        result = await paymant_order_txt(credits_list, date_order, number_order, session)

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }

