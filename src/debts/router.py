from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic.types import List

from src.database import get_async_session
from src.debts.models import *
from src.debts.schemas import CessionSchema, CessionCreate


router_cession = APIRouter(
    prefix="/Cession",
    tags=["Debts"]
)


# Получить цессии
@router_cession.get("/")
async def get_cession(credit_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            cession_query = await session.execute(select(credit.c.cession_id).where(credit.c.id == credit_id))
            cession_id = cession_query.one()[0]
            query = select(cession).where(cession.c.id == int(cession_id))
        else:
            query = select(cession)

        answer = await session.execute(query)
        result = [dict(r._mapping) for r in answer]
        return {
            'status': 'success',
            'data': result,
            'details': None
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Добавить/изменить цессию
@router_cession.post("/")
async def add_cession(new_cession: CessionCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_cession.model_dump()

    try:

        if req_data["id"]:
            cession_id = int(req_data["id"])
            data = {
                    "name": req_data["name"],
                    "number": req_data["number"],
                    "date": req_data["date"],
                    "summa": req_data["summa"],
                    "cedent": req_data["cedent"],
                    "cessionari": req_data["cessionari"],
                    "date_old_cession": req_data['date_old_cession'],
                    }
            post_data = update(cession).where(cession.c.id == cession_id).values(data)
        else:
            data = {"name": req_data["name"],
                    "number": req_data["number"],
                    "date": req_data["date"],
                    "summa": req_data["summa"],
                    "cedent": req_data["cedent"],
                    "cessionari": req_data["cessionari"],
                    "date_old_cession": req_data['date_old_cession'],
                    }
            post_data = insert(cession).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Цессия успешно сохранена'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


router_debtor = APIRouter(
    prefix="/Debtor",
    tags=["Debts"]
)


@router_debtor.get("/")
async def get_debtor(page: int, per_page: int, session: AsyncSession = Depends(get_async_session)):

    try:
        items = select(debtor).limit(per_page).offset((page - 1) * per_page)

        total = await session.execute(func.count(distinct(debtor.c.id)))

        answer = await session.execute(items)
        result = [dict(r._mapping) for r in answer]

        return {
            'status': 'success',
            'data': result,
            'details': {"total": total}
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }





# class CessionInfoAPIView(APIView):
#
#     @swagger_auto_schema(
#         method='get',
#         tags=['Карточка должника'],
#         operation_description="Получить информацию о цессии",
#         manual_parameters=[
#             openapi.Parameter('credit_id', openapi.IN_QUERY, description="Идентификатор кредита",
#                               type=openapi.TYPE_INTEGER),
#         ])
#
#     @action(detail=False, methods=['get'])
#     def get(self, request):
#         credit_id = request.query_params.get('credit_id')
#
#         if credit_id is not None:
#             cession_id = Credits.objects.get(pk=credit_id).cession_id
#             cession_set = Cession.objects.values().filter(pk=cession_id)
#         else:
#             cession_set = Cession.objects.values()
#
#         result = []
#         for cession in cession_set:
#             result.append({
#                 'id': cession['id'],
#                 'nameCes': cession['name'],
#                 'numberCes': cession['number'],
#                 'dateCes': cession['date'],
#                 'summaCes': cession['summa'],
#                 'cedent': cession['cedent'],
#                 'cessionari': cession['cessionari'],
#                 'oldCession': cession['date_old_cession'],
#             })
#
#         return Response(result)
#
#     @swagger_auto_schema(
#         methods=['post'],
#         tags=['Карточка должника'],
#         operation_description="Изменить данные о цессии",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'cession_json': openapi.Schema(type=openapi.TYPE_OBJECT, description='Данные цессии'),
#             }
#         ))
#     @action(methods=['post'], detail=True)
#     def post(self, request):
#         req_data = request.data
#
#         data = {"id": req_data["cession_json"]["id"],
#                 "name": req_data["cession_json"]["nameCes"],
#                 "number": req_data["cession_json"]["numberCes"],
#                 "date": req_data["cession_json"]["dateCes"],
#                 "summa": req_data["cession_json"]["summaCes"],
#                 "cedent": req_data["cession_json"]["cedent"],
#                 "cessionari": req_data["cession_json"]["cessionari"],
#                 "date_old_cession": req_data["cession_json"]['oldCession']}
#
#         path_cession = None
#         # path_cession = create_dir_cession(data)
#
#         serializers = CessionSerializer(data=data)
#         serializers.is_valid(raise_exception=True)
#         try:
#             Cession.objects.update_or_create(
#                 pk=data['id'],
#                 defaults={"name": data['name'],
#                           "number": data['number'],
#                           "date": data['date'],
#                           "summa": data['summa'],
#                           "cedent": data['cedent'],
#                           "cessionari": data['cessionari'],
#                           "date_old_cession": data['date_old_cession'],
#                           "path": path_cession},
#             )
#         except Exception as ex:
#             return Response({"error": f"Ошибка при добавлении/изменении данных. {ex}"})
#
#         return Response({'message': 'Цессия успешно сохранена'})
#
#
# def create_dir_cession(data):
#     base_path = os.path.dirname(os.path.realpath(__import__("__main__").__file__))
#
#     name_cession = f"{data['name']}_{data['number']}"
#     directory_cession = f'{base_path}/data/cession/{name_cession}'
#
#     if not os.path.exists(directory_cession):
#         os.mkdir(directory_cession)
#
#     path_cession = Path(directory_cession)
#
#     return path_cession