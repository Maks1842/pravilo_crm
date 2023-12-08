from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.registries.models import registry_headers, registry_structures, registry_filters
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
        for item in registry_query.mappings().all():
            if item.employ_registry:
                result.append({
                    "id": item.id,
                    "model": item.model,
                    "name_field": item.name_field,
                    "headers": item.headers,
                    "headers_key": item.headers_key,
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
            # "employ_registry": req_data["employ_registry"],
        }

        if req_data["id"]:
            reg_head_id: int = req_data["id"]
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


# Получить/добавить список Структур реестра
router_registry_structures = APIRouter(
    prefix="/v1/RegistryStructures",
    tags=["Registries"]
)


@router_registry_structures.get("/")
async def get_registry_structures(session: AsyncSession = Depends(get_async_session)):
    try:
        query = await session.execute(select(registry_structures))

        result = []
        for item in query.mappings().all():

            result.append({
                "text": item.name,
                "value": {
                    "reg_struct_id": item.id,
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
            reg_struct_id: int = data_dict['name']['value']['reg_struct_id']
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


# Получить json Структуры реестра
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


# Получить/добавить список Фильтров Реестра
router_registry_filters = APIRouter(
    prefix="/v1/RegistryFilters",
    tags=["Registries"]
)


@router_registry_filters.get("/")
async def get_registry_filters(type_filter_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if type_filter_id:
            query = await session.execute(select(registry_filters).where(registry_filters.c.type_filter_id == type_filter_id))
        else:
            query = await session.execute(select(registry_filters))

        result = []
        for item in query.mappings().all():

            result.append({
                "text": item.name,
                "value": {
                    "filter_id": item.id,
                    "type_filter_id": item.type_filter_id,
                    "reg_struct_id": item.registry_structure_id,
                    "function_name": item.function_name,
                    "comment": item.comment,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_registry_filters.post("/")
async def add_registry_filters(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    try:
        data = {
            "name": data_json['name'],
            "function_name": data_json['function_name'],
            "registry_structure_id": data_json['reg_struct_id'],
            "comment": data_json['comment'],
        }

        if data_json['id']:
            reg_filter_id: int = data_json['id']
            post_data = update(registry_filters).where(registry_filters.c.id == reg_filter_id).values(data)
        else:
            post_data = insert(registry_filters).values(data)

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