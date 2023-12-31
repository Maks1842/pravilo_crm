from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.references.models import *
from src.references.schemas import *

from src.routers_helper.rout_scraping.gaspravosudie_tribunals import parse_sudrf_index, parse_ej_sudrf
from src.routers_helper.rout_scraping.rosp_helper import extract_rosp_excel


# Получить/добавить взыскателей по ИД
router_ref_claimer_ed = APIRouter(
    prefix="/v1/RefClaimerED",
    tags=["References"]
)


@router_ref_claimer_ed.get("/")
async def get_claimer_ed(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_claimer_ed))

        result = []
        for item in query.mappings().all():

            result.append({
                "claimer_ed": item.name,
                "value": {"claimer_ed_id": item.id},
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }



# Получить/добавить Причина отзыва ИД
router_ref_reason_cansel_ed = APIRouter(
    prefix="/v1/RefReasonCanselED",
    tags=["References"]
)


@router_ref_reason_cansel_ed.get("/")
async def get_reason_cansel_ed(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_reason_cansel_ed))

        result = []
        for item in query.mappings().all():

            result.append({
                "reason_cansel_ed": item.name,
                "value": {"reason_cansel_ed_id": item.id},
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Суды
router_ref_tribunal = APIRouter(
    prefix="/v1/RefTribunals",
    tags=["References"]
)


@router_ref_tribunal.get("/")
async def get_tribunal(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.name.icontains(fragment)))

        result = []
        for item in query.mappings().all():

            if item['gaspravosudie'] == True:
                gaspravosudie = 'Возможна подача через ГАС'
            else:
                gaspravosudie = 'НЕ возможна подача через ГАС'

            result.append({
                "tribunal_name": item.name,
                "value": {
                    "tribunal_id": item.id,
                    "class_code": item["class_code"],
                    "oktmo": item["oktmo"],
                    "address": item["address"],
                    "email": item["email"],
                    "phone": item["phone"],
                    "gaspravosudie": gaspravosudie,
                    "gaspravosudie_value": item['gaspravosudie']
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_tribunal.post("/")
async def add_tribunal(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    # Первичная загрузка списка Судов, с помощью helper. В боевом режиме отключить
    # await parse_sudrf_index(session)

    # Загрузка списка Судов, в которые возможна подача через ГАС, с помощью helper. В боевом режиме отключить
    # await parse_ej_sudrf(session)
    # #
    # return

    req_data = data_json['data_json']

    try:
        data = {
            "name": req_data['name'],
            "class_code": req_data['class_code'],
            "oktmo": req_data['oktmo'],
            "address": req_data['address'],
            "email": req_data['email'],
            "phone": req_data['phone'],
            "gaspravosudie": req_data['gaspravosudie'],
        }
        if req_data["id"]:
            tribunal_id = int(req_data["id"])
            post_data = update(ref_tribunal).where(ref_tribunal.c.id == tribunal_id).values(data)
        else:
            post_data = insert(ref_tribunal).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Суд успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить Финансовый управляющий
router_ref_financial_manager = APIRouter(
    prefix="/v1/RefFinancialManager",
    tags=["References"]
)


@router_ref_financial_manager.get("/")
async def get_financial_manager(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_financial_manager))

        result = []
        for item in query.mappings().all():

            result.append({
                "fin_man_name": item.name,
                "value": {
                    "fin_man_id": item.id,
                    "organisation_fm": item["organisation_fm"],
                    "address_1": item["address_1"],
                    "address_2": item["address_2"],
                    "email": item["email"],
                    "phone": item['phone'],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Тип департамента предъявления ИД
router_ref_type_department = APIRouter(
    prefix="/v1/RefTypeDepartmentMov",
    tags=["References"]
)


@router_ref_type_department.get("/")
async def get_type_department(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_type_department))

        result = []
        for item in query.mappings().all():

            result.append({
                "type_department_name": item.name,
                "value": {
                    "type_department_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_type_department.post("/")
async def add_type_department(new_type_department: RefTypeDepartmentMovCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_type_department.model_dump()

    try:
        data = {
            "name": req_data['type_department_name'],
        }
        if req_data["id"]:
            type_department_id = int(req_data["id"])
            post_data = update(ref_type_department).where(ref_type_department.c.id == type_department_id).values(data)
        else:
            post_data = insert(ref_type_department).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Тип департамента успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить Регионы
router_ref_region = APIRouter(
    prefix="/v1/RefRegions",
    tags=["References"]
)


@router_ref_region.get("/")
async def get_region(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_region))

        result = []
        for item in query.mappings().all():

            result.append({
                "region": item.name,
                "value": {
                    "region_id": item.id,
                    "index": item["index"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_region.post("/")
async def add_region(new_region: RefRegionCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_region.model_dump()

    try:
        data = {
            "name": req_data['region'],
            "index": req_data['index'],
        }
        if req_data["id"]:
            region_id = int(req_data["id"])
            post_data = update(ref_region).where(ref_region.c.id == region_id).values(data)
        else:
            post_data = insert(ref_region).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Регион успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить РОСП
router_ref_rosp = APIRouter(
    prefix="/v1/RefRosp",
    tags=["References"]
)


@router_ref_rosp.get("/")
async def get_rosp(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_rosp).where(ref_rosp.c.name.icontains(fragment)))

        result = []
        for item in query.mappings().all():

            result.append({
                "rosp_name": item.name,
                "value": {
                    "rosp_id": item.id,
                    "type_department_id": item["type_department_id"],
                    "address": item["address"],
                    "address_index": item["address_index"],
                    "region_id": item["region_id"],
                    "phone": item['phone'],
                    "email": item["email"],
                    "class_code": item["class_code"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_rosp.post("/")
async def add_rosp(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    # # Первичная загрузка списка РОСП, с помощью helper. В боевом режиме отключить
    # await extract_rosp_excel(session)
    # return

    req_data = data_json['data_json']

    try:
        data = {
            "name": req_data['rosp_name'],
            "type_department_id": req_data['type_department_id'],
            "address": req_data['address'],
            "address_index": req_data['address_index'],
            "region_id": req_data['region_id'],
            "phone": req_data['phone'],
            "email": req_data['email'],
            "class_code": req_data['class_code'],
        }
        if req_data["id"]:
            rosp_id = int(req_data["id"])
            post_data = update(ref_rosp).where(ref_rosp.c.id == rosp_id).values(data)
        else:
            post_data = insert(ref_rosp).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'РОСП успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить Банк
router_ref_bank = APIRouter(
    prefix="/v1/RefBank",
    tags=["References"]
)


@router_ref_bank.get("/")
async def get_bank(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_bank).where(ref_bank.c.name.icontains(fragment)))

        result = []
        for item in query.mappings().all():

            result.append({
                "bank_name": item.name,
                "value": {
                    "bank_id": item.id,
                    "type_department_id": item["type_department_id"],
                    "address": item["address"],
                    "address_index": item["address_index"],
                    "region_id": item["region_id"],
                    "phone": item['phone'],
                    "email": item["email"],
                    "bik": item["bik"],
                    "inn": item["inn"],
                    "corr_account": item["corr_account"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_bank.post("/")
async def add_bank(new_bank: RefBankCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_bank.model_dump()

    try:
        data = {
            "name": req_data['bank_name'],
            "type_department_id": req_data['type_department_id'],
            "address": req_data['address'],
            "address_index": req_data['address_index'],
            "region_id": req_data['region_id'],
            "phone": req_data['phone'],
            "email": req_data['email'],
            "bik": req_data['bik'],
            "inn": req_data['inn'],
            "corr_account": req_data['corr_account'],
        }
        if req_data["id"]:
            bank_id = int(req_data["id"])
            post_data = update(ref_bank).where(ref_bank.c.id == bank_id).values(data)
        else:
            post_data = insert(ref_bank).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Банк успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить ПФР/ИФНС
router_ref_pfr = APIRouter(
    prefix="/v1/RefPfr",
    tags=["References"]
)


@router_ref_pfr.get("/")
async def get_pfr(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_pfr).where(ref_pfr.c.name.icontains(fragment)))

        result = []
        for item in query.mappings().all():

            result.append({
                "pfr_name": item.name,
                "value": {
                    "pfr_id": item.id,
                    "type_department_id": item["type_department_id"],
                    "address": item["address"],
                    "address_index": item["address_index"],
                    "region_id": item["region_id"],
                    "phone": item['phone'],
                    "email": item["email"],
                    "class_code": item["class_code"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_pfr.post("/")
async def add_pfr(new_pfr: RefPfrCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_pfr.model_dump()

    try:
        data = {
            "name": req_data['pfr_name'],
            "type_department_id": req_data['type_department_id'],
            "address": req_data['address'],
            "address_index": req_data['address_index'],
            "region_id": req_data['region_id'],
            "phone": req_data['phone'],
            "email": req_data['email'],
            "class_code": req_data['class_code'],
        }
        if req_data["id"]:
            pfr_id = int(req_data["id"])
            post_data = update(ref_pfr).where(ref_pfr.c.id == pfr_id).values(data)
        else:
            post_data = insert(ref_pfr).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'ПФР/ИФНС успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить/добавить Причина окончания ИП
router_ref_reason_end_ep = APIRouter(
    prefix="/v1/RefReasonEndEP",
    tags=["References"]
)


@router_ref_reason_end_ep.get("/")
async def get_reason_end_ep(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_reason_end_ep))

        result = []
        for item in query.mappings().all():

            result.append({
                "reason_end_ep": item.name,
                "value": {
                    "reason_end_ep_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Тип обращения
router_ref_type_statement = APIRouter(
    prefix="/v1/RefTypeStatement",
    tags=["References"]
)


@router_ref_type_statement.get("/")
async def get_type_statement(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_type_statement))

        result = []
        for item in query.mappings().all():

            result.append({
                "type_statement": item.name,
                "value": {
                    "type_statement_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Тип госпошлины
router_ref_type_state_duty = APIRouter(
    prefix="/v1/RefTypeStateDuty",
    tags=["References"]
)


@router_ref_type_state_duty.get("/")
async def get_type_state_duty(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_type_state_duty))

        result = []
        for item in query.mappings().all():

            result.append({
                "type_state_duty": item.name,
                "value": {
                    "type_state_duty_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Разделы карточки должника
router_ref_section_card_debtor = APIRouter(
    prefix="/v1/RefSectionCardDebtor",
    tags=["References"]
)


@router_ref_section_card_debtor.get("/")
async def get_section_card_debtor(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_section_card_debtor))

        result = []
        for item in query.mappings().all():

            result.append({
                "section_card_debtor": item.name,
                "value": {
                    "section_card_debtor_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Разделы юридической работы
router_ref_legal_section = APIRouter(
    prefix="/v1/RefLegalSection",
    tags=["References"]
)


@router_ref_legal_section.get("/")
async def get_legal_section(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_legal_section))

        result = []
        for item in query.mappings().all():

            result.append({
                "legal_section": item.name,
                "value": {
                    "legal_section_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Типы шаблонов документов
router_ref_type_templates = APIRouter(
    prefix="/v1/RefTypeTemplates",
    tags=["References"]
)


@router_ref_type_templates.get("/")
async def get_type_templates(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_type_templates))

        result = []
        for item in query.mappings().all():

            result.append({
                "type_template": item.name,
                "value": {
                    "type_template_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }





# Получить/добавить Варианты результатов/резолюций по обращениям
router_ref_result_statement = APIRouter(
    prefix="/v1/RefResultStatement",
    tags=["References"]
)


@router_ref_result_statement.get("/")
async def get_result_statement(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_result_statement))

        result = []
        for item in query.mappings().all():

            result.append({
                "result_statement": item.name,
                "value": {
                    "result_statement_id": item.id,
                    "type_statement_id": item["type_statement_id"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Типы фильтров
router_ref_type_filters = APIRouter(
    prefix="/v1/RefTypeFilters",
    tags=["References"]
)


@router_ref_type_filters.get("/")
async def get_type_filters(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_type_filter))

        result = []
        for item in query.mappings().all():

            result.append({
                "type_filter": item.name,
                "value": {
                    "type_filter_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }



