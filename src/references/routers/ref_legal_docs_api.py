from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.references.models import ref_legal_docs


# Получить/добавить Наименование юридических документов
router_ref_legal_docs = APIRouter(
    prefix="/v1/RefLegalDocs",
    tags=["References"]
)


@router_ref_legal_docs.get("/")
async def get_legal_docs(section_card_id: int = None, legal_section_id: int = None, session: AsyncSession = Depends(get_async_session)):

    try:
        if section_card_id:
            query = await session.execute(select(ref_legal_docs).where(or_(ref_legal_docs.c.section_card_id.in_([section_card_id, 1]),
                                                                           ref_legal_docs.c.section_card_id == None)))
        elif legal_section_id:
            query = await session.execute(select(ref_legal_docs).where(or_(ref_legal_docs.c.legal_section_id.in_([legal_section_id, 1]),
                                                                           ref_legal_docs.c.legal_section_id == None)))
        else:
            query = await session.execute(select(ref_legal_docs))

        result = []
        for item in query.mappings().all():

            result.append({
                "legal_docs": item.name,
                "value": {
                    "legal_docs_id": item.id,
                    "section_card_id": item.section_card_id,
                    "legal_section_id": item.legal_section_id,
                    "type_statement_id": item.type_statement_id,
                    "result_statement_id": item.type_statement_id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_legal_docs.post("/")
async def add_legal_docs(req_data: dict, session: AsyncSession = Depends(get_async_session)):

    try:
        data = {
            "name": req_data['name'],
            "section_card_id": req_data['section_card_id'],
            "legal_section_id": req_data['legal_section_id'],
            "type_statement_id": req_data['type_statement_id'],
            "result_statement_id": req_data['result_statement_id'],
        }
        if req_data["id"]:
            legal_docs_id = int(req_data["id"])
            post_data = update(ref_legal_docs).where(ref_legal_docs.c.id == legal_docs_id).values(data)
        else:
            post_data = insert(ref_legal_docs).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Наименование документа успешно сохранено'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Удалить Наименование юридического документа
router_delete_ref_legal_docs = APIRouter(
    prefix="/v1/DeleteRefLegalDocs",
    tags=["References"]
)


@router_delete_ref_legal_docs.delete("/")
async def delete_ref_legal_docs(item_id: int, session: AsyncSession = Depends(get_async_session)):

    try:
        await session.execute(delete(ref_legal_docs).where(ref_legal_docs.c.id == item_id))
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Объект успешно удален'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }