from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.registries.models import registry_headers, registry_structures
from src.registries.schemas import RegistryHeadersCreate


# Получить/добавить Наименования столбцов реестров
router_registry_headers = APIRouter(
    prefix="/v1/RegistryHeaders",
    tags=["Registries"]
)


@router_registry_headers.get("/")
async def get_registry_headers(session: AsyncSession = Depends(get_async_session)):
    try:
        registry_query = await session.execute(select(registry_headers).order_by(registry_headers.c.model))

        result = []
        for item in registry_query.all():

            item_registry = dict(item._mapping)

            result.append({
                "id": item_registry['id'],
                "model": item_registry['model'],
                "name_field": item_registry['name_field'],
                "headers": item_registry['headers'],
                "headers_key": item_registry['headers_key'],
                "excel_field": ""
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_registry_headers.post("/")
async def add_registry_headers(new_registry_headers: RegistryHeadersCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_registry_headers.model_dump()

    try:
        data = {
            "model": req_data["model"],
            "name_field": req_data["name_field"],
            "headers": req_data["headers"],
            "headers_key": req_data["headers_key"],
            "width_field": req_data["width_field"],
        }

        if req_data["id"]:
            reg_head_id = int(req_data["id"])
            post_data = update(registry_headers).where(registry_headers.c.id == reg_head_id).values(data)
        else:
            post_data = insert(registry_headers).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Данные успешно сохранены'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить список структур Реестра
router_registry_structures = APIRouter(
    prefix="/v1/RegistryStructures",
    tags=["Registries"]
)


@router_registry_structures.get("/")
async def get_registry_structures(session: AsyncSession = Depends(get_async_session)):
    try:
        query = await session.execute(select(registry_structures))

        result = []
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "text": item_dic['name'],
                "value": {
                    "reg_struct_id": item_dic["id"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_registry_structures.post("/")
async def add_registry_structures(data_dict: dict, session: AsyncSession = Depends(get_async_session)):

    try:
        data = {
            "name": data_dict['name']['text'],
            "items_json": data_dict['items_json'],
        }

        if data_dict['name']['value']['reg_struct_id']:
            reg_struct_id = int(data_dict['name']['value']['reg_struct_id'])
            post_data = update(registry_structures).where(registry_structures.c.id == reg_struct_id).values(data)
        else:
            post_data = insert(registry_structures).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Данные успешно сохранены'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить json структуры Реестра
router_registry_structur_json = APIRouter(
    prefix="/v1/RegistryStructurJSON",
    tags=["Registries"]
)


@router_registry_structur_json.get("/")
async def get_registry_structur_json(reg_struct_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        query = await session.execute(select(registry_structures.c.items_json).where(registry_structures.c.id == reg_struct_id))

        result = query.scalar()

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }