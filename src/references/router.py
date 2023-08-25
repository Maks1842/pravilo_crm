from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.references.models import *
from src.references.schemas import *


# Получить/добавить статус КД
router_ref_status_credit = APIRouter(
    prefix="/v1/RefStatusCredit",
    tags=["References"]
)


@router_ref_status_credit.get("/")
async def get_status_cd(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_status_credit))

        result = []
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "status_cd": item_dic['name'],
                "value": {"status_cd_id": item_dic['id']},
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_ref_status_credit.post("/")
async def add_status_cd(new_status_credit: RefStatusCreditCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_status_credit.model_dump()

    try:
        data = {
            "name": req_data["name"],
        }

        if req_data["id"]:
            status_cd_id = int(req_data["id"])
            post_data = update(ref_status_credit).where(ref_status_credit.c.id == status_cd_id).values(data)
        else:
            post_data = insert(ref_status_credit).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Статус КД успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "claimer_ed": item_dic['name'],
                "value": {"claimer_ed_id": item_dic['id']},
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить тип ИД
router_ref_type_ed = APIRouter(
    prefix="/v1/RefTypeED",
    tags=["References"]
)


@router_ref_type_ed.get("/")
async def get_type_ed(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_type_ed))

        result = []
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "type_ed": item_dic['name'],
                "value": {"type_ed_id": item_dic['id']},
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить статус ИД
router_ref_status_ed = APIRouter(
    prefix="/v1/RefStatusED",
    tags=["References"]
)


@router_ref_status_ed.get("/")
async def get_status_ed(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_status_ed))

        result = []
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "status_ed": item_dic['name'],
                "value": {"status_ed_id": item_dic['id']},
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "reason_cansel_ed": item_dic['name'],
                "value": {"reason_cansel_ed_id": item_dic['id']},
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
        for item in query.all():
            item_dic = dict(item._mapping)

            if item_dic['gaspravosudie'] == True:
                gaspravosudie = 'Возможна подача через ГАС'
            else:
                gaspravosudie = 'НЕ возможна подача через ГАС'

            result.append({
                "tribunal_name": item_dic['name'],
                "value": {
                    "tribunal_id": item_dic["id"],
                    "address": item_dic["address"],
                    "email": item_dic["email"],
                    "phone": item_dic["phone"],
                    "gaspravosudie": gaspravosudie,
                    "gaspravosudie_value": item_dic['gaspravosudie']
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
async def add_tribunal(new_tribunal: RefTribunalCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_tribunal.model_dump()

    try:
        data = {
            "name": req_data['tribunal_name'],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "fin_man_name": item_dic['name'],
                "value": {
                    "fin_man_id": item_dic["id"],
                    "organisation_fm": item_dic["organisation_fm"],
                    "address_1": item_dic["address_1"],
                    "address_2": item_dic["address_2"],
                    "email": item_dic["email"],
                    "phone": item_dic['phone'],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "type_department_name": item_dic['name'],
                "value": {
                    "type_department_id": item_dic["id"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "region": item_dic['name'],
                "value": {
                    "region_id": item_dic["id"],
                    "index": item_dic["index"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "rosp_name": item_dic['name'],
                "value": {
                    "rosp_id": item_dic["id"],
                    "type_department_id": item_dic["type_department_id"],
                    "address": item_dic["address"],
                    "address_index": item_dic["address_index"],
                    "region_id": item_dic["region_id"],
                    "phone": item_dic['phone'],
                    "email": item_dic["email"],
                    "class_code": item_dic["class_code"],
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
async def add_rosp(new_rosp: RefRospCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_rosp.model_dump()

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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "bank_name": item_dic['name'],
                "value": {
                    "bank_id": item_dic["id"],
                    "type_department_id": item_dic["type_department_id"],
                    "address": item_dic["address"],
                    "address_index": item_dic["address_index"],
                    "region_id": item_dic["region_id"],
                    "phone": item_dic['phone'],
                    "email": item_dic["email"],
                    "bik": item_dic["bik"],
                    "inn": item_dic["inn"],
                    "corr_account": item_dic["corr_account"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "pfr_name": item_dic['name'],
                "value": {
                    "pfr_id": item_dic["id"],
                    "type_department_id": item_dic["type_department_id"],
                    "address": item_dic["address"],
                    "address_index": item_dic["address_index"],
                    "region_id": item_dic["region_id"],
                    "phone": item_dic['phone'],
                    "email": item_dic["email"],
                    "class_code": item_dic["class_code"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "reason_end_ep": item_dic['name'],
                "value": {
                    "reason_end_ep_id": item_dic["id"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "type_statement": item_dic['name'],
                "value": {
                    "type_statement_id": item_dic["id"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "type_state_duty": item_dic['name'],
                "value": {
                    "type_state_duty_id": item_dic["id"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "section_card_debtor": item_dic['name'],
                "value": {
                    "section_card_debtor_id": item_dic["id"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "legal_section": item_dic['name'],
                "value": {
                    "legal_section_id": item_dic["id"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "type_templates": item_dic['name'],
                "value": {
                    "type_templates_id": item_dic["id"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Наименование юридических документов
router_ref_legal_docs = APIRouter(
    prefix="/v1/RefLegalDocs",
    tags=["References"]
)


@router_ref_legal_docs.get("/")
async def get_legal_docs(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_legal_docs))

        result = []
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "legal_docs": item_dic['name'],
                "value": {
                    "legal_docs_id": item_dic["id"],
                    "section_card_id": item_dic["section_card_id"],
                    "legal_section_id": item_dic["legal_section_id"],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "result_statement": item_dic['name'],
                "value": {
                    "result_statement_id": item_dic["id"],
                    "type_statement_id": item_dic["type_statement_id"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить Виды задач
router_ref_task = APIRouter(
    prefix="/v1/RefTask",
    tags=["References"]
)


@router_ref_task.get("/")
async def get_task(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(ref_task))

        result = []
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "task_name": item_dic['name'],
                "value": {
                    "task_name_id": item_dic["id"],
                    "section_card_id": item_dic["section_card_id"],
                    "type_statement_id": item_dic["type_statement_id"],
                    "legal_doc_id": item_dic["legal_doc_id"],
                    "result_statement_id": item_dic["result_statement_id"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }



