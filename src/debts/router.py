import re

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.references.models import ref_status_credit
from src.debts.schemas import CessionCreate, CreditCreate


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
            cession_item = cession_query.one()
            cession_id = dict(cession_item._mapping)

            query = select(cession).where(cession.c.id == int(cession_id['cession_id']))
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


router_credits = APIRouter(
    prefix="/Credit",
    tags=["Debts"]
)


# Получить кредиты
@router_credits.get("/")
async def get_credits(credit_id: int = None, debtor_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            query = select(credit).where(credit.c.id == credit_id)
        else:
            query = select(credit).where(credit.c.debtor_id == debtor_id)

        answer = await session.execute(query)

        result = []
        for item in answer.all():
            data = dict(item._mapping)

            status_query = await session.execute(select(ref_status_credit).where(ref_status_credit.c.id == int(data['status_cd_id'])))
            status_set = dict(status_query.one()._mapping)
            status = status_set['name']

            result.append({
                'id': data['id'],
                'debtor_id': data['debtor_id'],
                'status_cd': status,
                'status_cd_id': data['status_cd_id'],
                'creditor': data['creditor'],
                'number': data['number'],
                'date_start': data['date_start'],
                'date_end': data['date_end'],
                'summa': data['summa'],
                'summa_by_cession': data['summa_by_cession'],
                'interest_rate': data['interest_rate'],
                'percent_of_od': data['percent_of_od'],
                'overdue_od': data['overdue_od'],
                'overdue_percent': data['overdue_percent'],
                'penalty': data['penalty'],
                'gov_toll': data['gov_toll'],
                'cession_id': data['cession_id'],
                'balance_debt': data['balance_debt'],
                'credits_old': data['credits_old'],
                'comment': data['comment'],
            })
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


# Изменить данные о КД
@router_credits.post("/")
async def add_credits(new_credit: CreditCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_credit.model_dump()

    try:
        if req_data["id"]:
            credit_id = int(req_data["id"])
            data = {
                "creditor": req_data["creditor"],
                "number": req_data["number"],
                "date_start": req_data["date_start"],
                "date_end": req_data["date_end"],
                "summa_by_cession": req_data["summa_by_cession"],
                "summa": req_data["summa"],
                "interest_rate": req_data['interest_rate'],
                "overdue_od": req_data["overdue_od"],
                "overdue_percent": req_data["overdue_percent"],
                "penalty": req_data["penalty"],
                "percent_of_od": req_data["percent_of_od"],
                "gov_toll": req_data["gov_toll"],
                "balance_debt": req_data["balance_debt"],
                "debtor_id": req_data['debtor_id'],
                "cession_id": req_data["cession_id"],
                "status_cd_id": req_data["status_cd_id"],
                "comment": req_data["comment"],
                "credits_old": req_data["credits_old"],
            }

            # Не срабатывает исключение, если нет указанного id в БД
            post_data = update(credit).where(credit.c.id == credit_id).values(data)
        else:
            data = {
                "creditor": req_data["creditor"],
                "number": req_data["number"],
                "date_start": req_data["date_start"],
                "date_end": req_data["date_end"],
                "summa_by_cession": req_data["summa_by_cession"],
                "summa": req_data["summa"],
                "interest_rate": req_data['interest_rate'],
                "overdue_od": req_data["overdue_od"],
                "overdue_percent": req_data["overdue_percent"],
                "penalty": req_data["penalty"],
                "percent_of_od": req_data["percent_of_od"],
                "gov_toll": req_data["gov_toll"],
                "balance_debt": req_data["balance_debt"],
                "debtor_id": req_data['debtor_id'],
                "cession_id": req_data["cession_id"],
                "status_cd_id": req_data["status_cd_id"],
                "comment": req_data["comment"],
                "credits_old": req_data["credits_old"],
                    }
            post_data = insert(credit).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': data,
            'details': 'Кредит успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


router_credit_debtor = APIRouter(
    prefix="/GetCreditDebtor",
    tags=["Debts"]
)


# Получить ФИО + КД
@router_credit_debtor.get("/")
async def get_credit_debtor(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        if re.findall(r'\d+', fragment):
            credits_query = await session.execute(select(credit).where(credit.c.number.icontains(fragment)))
            credits_set = credits_query.all()
        else:
            debtors_query = await session.execute(select(debtor))
            debtors_set = debtors_query.all()



            debtors_id = ()
            for item in debtors_set:

                debtor_item = dict(item._mapping)

                if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
                    fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                          f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
                else:
                    fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

                if re.findall(rf'(?i){fragment}', fio):
                    debtors_id = debtors_id + (debtor_item['id'],)

            credits_query = await session.execute(select(credit).where(credit.c.debtor_id.in_(debtors_id)))
            credits_set = credits_query.all()

        result = []
        for item_cd in credits_set:

            credit_item = dict(item_cd._mapping)

            number = credit_item['number']

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item['debtor_id'])))
            debtor_set = debtor_query.one()
            debtor_item = dict(debtor_set._mapping)

            value_id = {"credit_id": credit_item['id'],
                        "debtor_id": debtor_item['id']}

            if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
                fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                      f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
            else:
                fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

            result.append({
                "value": value_id,
                "text": f'{fio}, {number}',
            })
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


router_debtor_inn = APIRouter(
    prefix="/GetDebtorInn",
    tags=["Debts"]
)


# Получить ФИО + ИНН
@router_debtor_inn.get("/")
async def get_debtor_inn(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:



        if re.findall(r'\d+', fragment):
            debtors_query = await session.execute(select(debtor).where(debtor.c.inn.icontains(fragment)))
            debtors_set = debtors_query.all()
        else:
            debtors_query = await session.execute(select(debtor))
            debtors_set = debtors_query.all()

            debtors_id = ()
            for item in debtors_set:

                debtor_item = dict(item._mapping)

                if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
                    fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                          f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
                else:
                    fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

                if re.findall(rf'(?i){fragment}', fio):
                    debtors_id = debtors_id + (debtor_item['id'],)

            debtors_query = await session.execute(select(debtor).where(debtor.c.id.in_(debtors_id)))
            debtors_set = debtors_query.all()

        result = []
        for item_debt in debtors_set:

            debtor_item = dict(item_debt._mapping)

            inn = debtor_item['inn']

            if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
                fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                      f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
            else:
                fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

            result.append({
                "debtor_id": debtor_item['id'],
                "text": f'{fio}, {inn}',
            })
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


router_debt_information = APIRouter(
    prefix="/GetDebtInformation",
    tags=["Debts"]
)


# Получить информацию о долге
@router_debt_information.get("/")
async def get_debt_information(credit_id: int, session: AsyncSession = Depends(get_async_session)):

    try:
        credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
        credit_item = dict(credit_query.one()._mapping)

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item['debtor_id'])))
        debtor_item = dict(debtor_query.one()._mapping)

        cession_query = await session.execute(select(cession).where(cession.c.id == int(credit_item['cession_id'])))
        cession_item = dict(cession_query.one()._mapping)

        status_cd_query = await session.execute(select(ref_status_credit).where(ref_status_credit.c.id == int(credit_item['status_cd_id'])))
        status_cd_item = dict(status_cd_query.one()._mapping)
        status_cd = status_cd_item['name']

        summa_all = '0.00'
        summa_last = '0.00'
        date_last = ''
        ed_id = ''
        edType = ''
        edNum = ''
        edSumma = '0.00'
        edSuccession = ''
        claimer_ep = ''
    except:
        pass

    #     payment_query = await session.execute(select(payment).where(payments.c.id == int(credit_item['cession_id'])))
    #     payments_set = payment_query.all()
    #
    #     if data['type_ed_id'] is not None and data['type_ed_id'] != '':
    #         type_ed_query = await session.execute(select(ref_type_ed).where(ref_type_ed.c.id == int(data['type_ed_id'])))
    #         type_ed = dict(type_ed_query.one()._mapping)
    #
    #         type_ed = type_ed['name']
    #         type_ed_id = type_ed['id']
    #
    #
    #
    #     if re.findall(r'\d+', fragment):
    #         debtors_query = await session.execute(select(debtor).where(debtor.c.inn.icontains(fragment)))
    #         debtors_set = debtors_query.all()
    #     else:
    #         debtors_query = await session.execute(select(debtor))
    #         debtors_set = debtors_query.all()
    #
    #         debtors_id = ()
    #         for item in debtors_set:
    #
    #             debtor_item = dict(item._mapping)
    #
    #             if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
    #                 fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
    #                       f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
    #             else:
    #                 fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"
    #
    #             if re.findall(rf'(?i){fragment}', fio):
    #                 debtors_id = debtors_id + (debtor_item['id'],)
    #
    #         debtors_query = await session.execute(select(debtor).where(debtor.c.id.in_(debtors_id)))
    #         debtors_set = debtors_query.all()
    #
    #     result = []
    #     for item_debt in debtors_set:
    #
    #         debtor_item = dict(item_debt._mapping)
    #
    #         inn = debtor_item['inn']
    #
    #         if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
    #             fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
    #                   f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
    #         else:
    #             fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"
    #
    #         result.append({
    #             "debtor_id": debtor_item['id'],
    #             "text": f'{fio}, {inn}',
    #         })
    #     return {
    #         'status': 'success',
    #         'data': result,
    #         'details': None
    #     }
    # except Exception as ex:
    #     return {
    #         "status": "error",
    #         "data": None,
    #         "details": ex
    #     }











# Получить должников + пагинация
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