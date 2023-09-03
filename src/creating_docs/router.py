from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.creating_docs.models import docs_generator_template
from src.creating_docs.schemas import DocsGeneratorTemplateCreate


# Получить/добавить Шаблоны печатных форм
router_docs_generator_template = APIRouter(
    prefix="/v1/DocsGeneratorTemplate",
    tags=["GeneratorDocs"]
)


@router_docs_generator_template.get("/")
async def get_template_docs(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(docs_generator_template))

        result = []
        for item in query.mappings().all():

            result.append({
                "template_name": item['name'],
                "value": {"template_id": item['id'],
                          "type_template_id": item['type_template_id'],
                          "path_template_file": item['path_template_file']},
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_docs_generator_template.post("/")
async def add_template_docs(new_template_docs: DocsGeneratorTemplateCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_template_docs.model_dump()

    try:
        data = {
            "name": req_data["name"],
            "type_template_id": req_data["type_template_id"],
            "path_template_file": req_data["path_template_file"],
        }

        if req_data["id"]:
            template_doc_id = int(req_data["id"])
            post_data = update(docs_generator_template).where(docs_generator_template.c.id == template_doc_id).values(data)
        else:
            post_data = insert(docs_generator_template).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Шаблон документа успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }