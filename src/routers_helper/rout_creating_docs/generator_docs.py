import os

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit
from src.creating_docs.models import docs_generator_variable
from src.registries.models import registry_headers
from src.routers_helper.rout_registry.get_data_for_registry import calculation_of_filters
from src.routers_helper.rout_creating_docs.insert_into_docs import select_from_variables
from src.config import logging_path

import logging
log_path = os.path.join(logging_path, 'generator_docs.log')
logging.basicConfig(level=logging.DEBUG, filename=log_path, filemode="w", format='%(levelname)s; %(asctime)s; %(filename)s; %(message)s')

'''
Метод формирования документов (печатных форм) на основе имеющихся шаблонов
Метод принимает список credit_id по которым необходимо сформировать документы, 
а также данные о шаблоне, по которому формировать документ

Применяются дополнительные методы склонения по падежам
'''


# Сформировать печатные формы
router_generator_docs = APIRouter(
    prefix="/v1/GeneratorDocs",
    tags=["GeneratorDocs"]
)


@router_generator_docs.post("/")
async def generator_docs(data_dict: dict, session: AsyncSession = Depends(get_async_session)):

    try:
        credits_id_array = data_dict['credits_id_array']
        template_json = data_dict['template_json']
        legal_number = data_dict['legal_number']

        credits_query = await session.execute(select(credit).where(credit.c.id.in_(credits_id_array)))
        credits_list = credits_query.mappings().all()

        headers_id_query = await session.execute(select(docs_generator_variable.c.registry_headers_id))
        headers_id_list = []
        for item in headers_id_query.mappings().all():
            headers_id_list.append(item['registry_headers_id'])

        headers_query = await session.execute(select(registry_headers).where(registry_headers.c.id.in_(headers_id_list)))
        headers_list = headers_query.mappings().all()

        values_for_generator = await calculation_of_filters(headers_list, credits_list, legal_number, session)

        result = await select_from_variables(values_for_generator, template_json, session)

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }

