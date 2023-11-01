import re
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import lending, cession, credit, debtor
from src.references.models import ref_status_credit, ref_type_ed, ref_tribunal
from src.debts.schemas import CessionCreate, CreditCreate
from src.payments.models import payment
from src.collection_debt.models import executive_document, executive_productions


# Получить/добавить Займы
router_lending = APIRouter(
    prefix="/v1/Lending",
    tags=["Debts"]
)


@router_lending.get("/")
async def get_lending(cession_id: int = None, session: AsyncSession = Depends(get_async_session)):

    summa = 0
    balance_debt = 0

    try:
        if cession_id:
            query = await session.execute(select(cession.c.lending_id).where(cession.c.id == cession_id))
            lending_id = query.scalar()

            lending_query = await session.execute(select(lending).where(lending.c.id == int(lending_id)))
        else:
            lending_query = await session.execute(select(lending))

        result = []
        for item in lending_query.mappings().all():

            if item.summa is not None:
                summa = item.summa / 100

            if item.balance_debt is not None:
                balance_debt = item.balance_debt / 100

            result.append({
                "id": item.id,
                "creditor": item.creditor,
                "number": item.number,
                "date_start": datetime.strptime(str(item.date_start), '%Y-%m-%d').strftime("%d.%m.%Y"),
                "summa": summa,
                "interest_rate": item.interest_rate,
                "date_end": datetime.strptime(str(item.date_end), '%Y-%m-%d').strftime("%d.%m.%Y"),
                "loan_repayment_procedure": item.loan_repayment_procedure,
                "dividends_payment_procedure": item.dividends_payment_procedure,
                "balance_debt": balance_debt,
                "comment": item.comment,
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_lending.post("/")
async def add_lending(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    req_data = data_json['data_json']

    try:
        summa = int(float(req_data["summa"]) * 100)
        balance_debt = int(float(req_data["balance_debt"]) * 100)
        interest_rate = float(req_data["interest_rate"])

        data = {
            "creditor": req_data["creditor"],
            "number": req_data["number"],
            "date_start": datetime.strptime(req_data["date_start"], '%Y-%m-%d').date(),
            "summa": summa,
            "interest_rate": interest_rate,
            "date_end": datetime.strptime(req_data["date_end"], '%Y-%m-%d').date(),
            "loan_repayment_procedure": req_data['loan_repayment_procedure'],
            "dividends_payment_procedure": req_data['dividends_payment_procedure'],
            "balance_debt": balance_debt,
            "comment": req_data['comment'],
        }

        if req_data["id"]:
            lending_id: int = req_data["id"]

            post_data = update(lending).where(lending.c.id == lending_id).values(data)
        else:
            post_data = insert(lending).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Займ успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить наименование Займов
router_get_lending_name = APIRouter(
    prefix="/v1/GetLendingName",
    tags=["Debts"]
)


@router_get_lending_name.get("/")
async def get_lending_name(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(lending))

        result = []
        for item in query.mappings().all():

            result.append({
                "creditor": item.creditor,
                "value": {
                    "lending_id": item.id,
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить цессию
router_cession = APIRouter(
    prefix="/v1/Cession",
    tags=["Debts"]
)


@router_cession.get("/")
async def get_cession(credit_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            query = await session.execute(select(credit.c.cession_id).where(credit.c.id == credit_id))
            cession_id = query.scalar()

            query = select(cession).where(cession.c.id == int(cession_id))
        else:
            query = select(cession)

        answer = await session.execute(query)
        result = []
        for item in answer.mappings().all():

            if item.summa is not None:
                summa = item.summa / 100
            else:
                summa = 0

            if item.lending_id is not None:
                lending_query = await session.execute(select(lending.c.creditor).where(lending.c.id == int(item.lending_id)))
                creditor = lending_query.scalar()
            else:
                creditor = None

            result.append({
                "id": item.id,
                "name": item.name,
                "number": item.number,
                "date": item.date,
                "summa": summa,
                "cedent": item.cedent,
                "cessionari": item.cessionari,
                "date_old_cession": item.date_old_cession,
                "lending_id": item.lending_id,
                "creditor": creditor
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_cession.post("/")
async def add_cession(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    req_data = data_json['data_json']

    try:
        summa = int(float(req_data["summa"]) * 100)

        data = {
            "name": req_data["name"],
            "number": req_data["number"],
            "date": datetime.strptime(req_data["date"], '%Y-%m-%d').date(),
            "summa": summa,
            "cedent": req_data["cedent"],
            "cessionari": req_data["cessionari"],
            "date_old_cession": req_data['date_old_cession'],
            "lending_id": req_data['lending_id'],
        }

        if req_data["id"]:
            cession_id = int(req_data["id"])

            # Не срабатывает исключение, если нет указанного id в БД
            post_data = update(cession).where(cession.c.id == cession_id).values(data)
        else:
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


# Получить наименование цессий
router_get_cession_name = APIRouter(
    prefix="/v1/GetCessionName",
    tags=["Debts"]
)


@router_get_cession_name.get("/")
async def get_cession_name(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(cession))

        result = []
        for item in query.mappings().all():

            result.append({
                "cession_name": item.name,
                "value": {
                    "item_id": item.id,
                    "model": 'credit',
                    "field": 'cession_id'
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить/добавить кредит
router_credits = APIRouter(
    prefix="/v1/Credit",
    tags=["Debts"]
)


@router_credits.get("/")
async def get_credits(credit_id: int = None, debtor_id: int = None, session: AsyncSession = Depends(get_async_session)):
    try:
        if credit_id:
            query = await session.execute(select(credit).where(credit.c.id == credit_id))
        else:
            query = await session.execute(select(credit).where(credit.c.debtor_id == debtor_id))

        result = []
        for data in query.mappings().all():

            status_query = await session.execute(select(ref_status_credit).where(ref_status_credit.c.id == int(data.status_cd_id)))
            status_set = status_query.mappings().one()
            status = status_set.name

            if data.summa is not None:
                summa = data.summa / 100
            else:
                summa = 0

            if data.summa_by_cession is not None:
                summa_by_cession = data.summa_by_cession / 100
            else:
                summa_by_cession = 0

            if data.percent_of_od is not None:
                percent_of_od = data.percent_of_od / 100
            else:
                percent_of_od = 0

            if data.overdue_od is not None:
                overdue_od = data.overdue_od / 100
            else:
                overdue_od = 0

            if data.overdue_percent is not None:
                overdue_percent = data.overdue_percent / 100
            else:
                overdue_percent = 0

            if data.penalty is not None:
                penalty = data.penalty / 100
            else:
                penalty = 0

            if data.gov_toll is not None:
                gov_toll = data.gov_toll / 100
            else:
                gov_toll = 0

            if data.balance_debt is not None:
                balance_debt = data.balance_debt / 100
            else:
                balance_debt = 0

            result.append({
                'id': data.id,
                'debtor_id': data.debtor_id,
                'status_cd': status,
                'status_cd_id': data.status_cd_id,
                'creditor': data.creditor,
                'number': data.number,
                'date_start': data.date_start,
                'date_end': data.date_end,
                'summa': summa,
                'summa_by_cession': summa_by_cession,
                'interest_rate': data.interest_rate,
                'percent_of_od': percent_of_od,
                'overdue_od': overdue_od,
                'overdue_percent': overdue_percent,
                'penalty': penalty,
                'gov_toll': gov_toll,
                'cession_id': data.cession_id,
                'balance_debt': balance_debt,
                'credits_old': data.credits_old,
                'comment': data.comment,
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_credits.post("/")
async def add_credits(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    req_data = data_json['data_json']

    summa = int(float(req_data["summa"]) * 100)
    summa_by_cession = int(float(req_data["summa_by_cession"]) * 100)
    overdue_od = int(float(req_data["overdue_od"]) * 100)
    overdue_percent = int(float(req_data["overdue_percent"]) * 100)
    penalty = int(float(req_data["penalty"]) * 100)
    percent_of_od = int(float(req_data["percent_of_od"]) * 100)
    gov_toll = int(float(req_data["gov_toll"]) * 100)
    balance_debt = int(float(req_data["balance_debt"]) * 100)

    try:
        data = {
            "creditor": req_data["creditor"],
            "number": req_data["number"],
            "date_start": datetime.strptime(req_data["date_start"], '%Y-%m-%d').date(),
            "date_end": req_data["date_end"],
            "summa_by_cession": summa_by_cession,
            "summa": summa,
            "interest_rate": req_data['interest_rate'],
            "overdue_od": overdue_od,
            "overdue_percent": overdue_percent,
            "penalty": penalty,
            "percent_of_od": percent_of_od,
            "gov_toll": gov_toll,
            "balance_debt": balance_debt,
            "debtor_id": req_data["debtor_id"],
            "cession_id": req_data["cession_id"],
            "status_cd_id": req_data["status_cd_id"],
            "comment": req_data["comment"],
            "credits_old": req_data["credits_old"],
            "parent_id": req_data["parent_id"],
        }

        if req_data["id"]:
            credit_id = int(req_data["id"])

            # Не срабатывает исключение, если нет указанного id в БД
            post_data = update(credit).where(credit.c.id == credit_id).values(data)
        else:
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


# Получить/добавить должника
router_debtor = APIRouter(
    prefix="/v1/Debtor",
    tags=["Debts"]
)


@router_debtor.get("/")
async def get_debtor(debtor_id: int = None, session: AsyncSession = Depends(get_async_session)):

    tribunal_id = None
    tribunal_name = None
    gaspravosudie = 'НЕ возможно'

    try:
        query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))

        result = []
        for item in query.mappings().all():
            if item.tribunal_id:
                tribunal_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == int(item.tribunal_id)))
                tribunal_set = tribunal_query.mappings().fetchone()

                if tribunal_set:
                    tribunal_id = tribunal_set.id
                    tribunal_name = tribunal_set.name
                    if tribunal_set.gaspravosudie:
                        gaspravosudie = 'Возможно'

            result.append({
                'id': item.id,
                'last_name_1': item.last_name_1,
                'first_name_1': item.first_name_1,
                'second_name_1': item.second_name_1,
                'last_name_2': item.last_name_2,
                'first_name_2': item.first_name_2,
                'second_name_2': item.second_name_2,
                'pol': item.pol,
                'birthday': item.birthday,
                'pensioner': item.pensioner,
                'place_of_birth': item.place_of_birth,
                'passport_series': item.passport_series,
                'passport_num': item.passport_num,
                'passport_date': item.passport_date,
                'passport_department': item.passport_department,
                'inn': item.inn,
                'snils': item.snils,
                'address_1': item.address_1,
                'address_2': item.address_2,
                'index_add_1': item.index_add_1,
                'index_add_2': item.index_add_2,
                'phone': item.phone,
                'email': item.email,
                'tribunal_id': tribunal_id,
                'tribunal_name': tribunal_name,
                'gaspravosudie': gaspravosudie,
                'comment': item.comment,
            })

        return result[0]
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_debtor.post("/")
async def add_debtor(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    debtor_data = data_json['data_json']

    try:
        data = {
            "last_name_1": debtor_data["last_name_1"],
            "first_name_1": debtor_data["first_name_1"],
            "second_name_1": debtor_data["second_name_1"],
            "last_name_2": debtor_data["last_name_2"],
            "first_name_2": debtor_data["first_name_2"],
            "second_name_2": debtor_data["second_name_2"],
            "pol": debtor_data["pol"],
            "birthday": datetime.strptime(debtor_data["birthday"], '%Y-%m-%d').date(),
            "pensioner": debtor_data["pensioner"],
            "place_of_birth": debtor_data["place_of_birth"],
            "passport_series": debtor_data["passport_series"],
            "passport_num": debtor_data["passport_num"],
            "passport_date": datetime.strptime(debtor_data["passport_date"], '%Y-%m-%d').date(),
            "passport_department": debtor_data["passport_department"],
            "inn": debtor_data["inn"],
            "snils": debtor_data["snils"],
            "address_1": debtor_data["address_1"],
            "address_2": debtor_data["address_2"],
            "index_add_1": debtor_data["index_add_1"],
            "index_add_2": debtor_data["index_add_2"],
            "phone": debtor_data["phone"],
            "email": debtor_data["email"],
            "tribunal_id": debtor_data["tribunal_id"],
            "comment": debtor_data["comment"],
        }

        if debtor_data["id"]:
            debtor_id = int(debtor_data["id"])

            # Не срабатывает исключение, если нет указанного id в БД
            post_data = update(debtor).where(debtor.c.id == debtor_id).values(data)
        else:
            post_data = insert(debtor).values(data)

        await session.execute(post_data)
        await session.commit()

        return {
            'status': 'success',
            'data': data,
            'details': 'Должник успешно сохранен'
        }
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении данных. {ex}"
        }


# Получить ФИО + КД
router_credit_debtor = APIRouter(
    prefix="/v1/GetCreditDebtor",
    tags=["Debts"]
)


@router_credit_debtor.get("/")
async def get_credit_debtor(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        if re.findall(r'\d+', fragment):
            credits_query = await session.execute(select(credit).where(credit.c.number.icontains(fragment)))
            credits_set = credits_query.mappings().all()
        else:
            debtors_query = await session.execute(select(debtor))
            debtors_set = debtors_query.mappings().all()

            debtors_id = ()
            for debtor_item in debtors_set:

                if debtor_item.last_name_2 is not None and debtor_item.last_name_2 != '':
                    fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                          f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
                else:
                    fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

                if re.findall(rf'(?i){fragment}', fio):
                    debtors_id = debtors_id + (debtor_item.id,)

            credits_query = await session.execute(select(credit).where(credit.c.debtor_id.in_(debtors_id)))
            credits_set = credits_query.mappings().all()

        result = []
        for credit_item in credits_set:

            number = credit_item.number

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item.debtor_id)))
            debtor_item = debtor_query.mappings().one()

            value_id = {"credit_id": credit_item.id,
                        "debtor_id": debtor_item.id}

            if debtor_item.last_name_2 is not None and debtor_item.last_name_2 != '':
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                      f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            result.append({
                "value": value_id,
                "text": f'{fio}, {number}',
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить ФИО + ИНН
router_debtor_inn = APIRouter(
    prefix="/v1/GetDebtorInn",
    tags=["Debts"]
)


@router_debtor_inn.get("/")
async def get_debtor_inn(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        if re.findall(r'\d+', fragment):
            debtors_query = await session.execute(select(debtor).where(debtor.c.inn.icontains(fragment)))
            debtors_set = debtors_query.mappings().all()
        else:
            debtors_query = await session.execute(select(debtor))
            debtors_set = debtors_query.mappings().all()

            debtors_id = ()
            for debtor_item in debtors_set:

                if debtor_item.last_name_2 is not None and debtor_item.last_name_2 != '':
                    fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                          f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
                else:
                    fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

                if re.findall(rf'(?i){fragment}', fio):
                    debtors_id = debtors_id + (debtor_item.id,)

            debtors_query = await session.execute(select(debtor).where(debtor.c.id.in_(debtors_id)))
            debtors_set = debtors_query.mappings().all()

        result = []
        for debtor_item in debtors_set:

            inn = debtor_item.inn

            if debtor_item.last_name_2 is not None and debtor_item.last_name_2 != '':
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                      f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            result.append({
                "debtor_id": debtor_item.id,
                "text": f'{fio}, {inn}',
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить ФИО
router_debtor_name = APIRouter(
    prefix="/v1/GetDebtorName",
    tags=["Debts"]
)


@router_debtor_name.get("/")
async def get_debtor_name(fragment: str, session: AsyncSession = Depends(get_async_session)):

    try:
        debtors_query = await session.execute(select(debtor).where(or_(debtor.c.last_name_1.icontains(fragment),
                                                                       debtor.c.first_name_1.icontains(fragment),
                                                                       debtor.c.second_name_1.icontains(fragment),
                                                                       debtor.c.last_name_2.icontains(fragment),
                                                                       debtor.c.first_name_2.icontains(fragment),
                                                                       debtor.c.second_name_2.icontains(fragment))))
        debtors_set = debtors_query.mappings().all()

        result = []
        for debtor_item in debtors_set:

            if debtor_item.last_name_2 is not None and debtor_item.last_name_2 != '':
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                      f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            result.append({
                "fio_debtor": fio,
                "value": {"item_id": debtor_item.id,
                          "model": 'credit',
                          "field": 'debtor_id'}})


        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить информацию о долге
router_debt_information = APIRouter(
    prefix="/v1/GetDebtInformation",
    tags=["Debts"]
)


@router_debt_information.get("/")
async def get_debt_information(credit_id: int, session: AsyncSession = Depends(get_async_session)):

    birthday = ''

    try:
        credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
        credit_item = credit_query.mappings().one()

        if credit_item.balance_debt is not None and credit_item.balance_debt != '':
            balance_debt = credit_item.balance_debt / 100
        else:
            balance_debt = 0

        if credit_item.summa_by_cession is not None and credit_item.summa_by_cession != '':
            summa_by_cession = credit_item.summa_by_cession / 100
        else:
            summa_by_cession = 0

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item.debtor_id)))
        debtor_item = debtor_query.mappings().one()

        cession_query = await session.execute(select(cession).where(cession.c.id == int(credit_item.cession_id)))
        cession_item = cession_query.mappings().one()

        status_cd_query = await session.execute(select(ref_status_credit).where(ref_status_credit.c.id == int(credit_item.status_cd_id)))
        status_cd_item = status_cd_query.mappings().one()
        status_cd = status_cd_item.name

        try:
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(payment.c.credit_id == credit_id))
            summa_all = summa_query.scalar() / 100

            pay_query = await session.execute(select(payment).where(payment.c.credit_id == credit_id).order_by(desc(payment.c.id)))
            payment_set = pay_query.mappings().first()
            pay_last = payment_set.summa / 100
            date_last = payment_set.date
        except:
            summa_all = 0
            pay_last = 0
            date_last = ''

        try:
            ed_query = await session.execute(select(executive_document).where(executive_document.c.credit_id == credit_id).order_by(desc(executive_document.c.id)))
            ed_set = ed_query.mappings().first()

            ed_type_query = await session.execute(select(ref_type_ed.c.name).where(ref_type_ed.c.id == int(ed_set.type_ed_id)))
            ed_type = ed_type_query.scalar()
            ed_id = ed_set.id
            edType = ed_type
            edNum = ed_set.number
            edSumma = ed_set.summa_debt_decision / 100
            edSuccession = ed_set.succession
        except:
            ed_id = None
            edType = ''
            edNum = ''
            edSumma = 0
            edSuccession = ''

        try:
            ep_query = await session.execute(select(executive_productions.c.claimer).where(executive_productions.c.credit_id == credit_id).order_by(desc(executive_productions.c.date_on)))
            claimer_ep = ep_query.scalar()
        except:
            claimer_ep = ''

        if debtor_item.last_name_2 is not None and debtor_item.last_name_2 != '':
            fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                  f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
        else:
            fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

        if debtor_item.passport_series is not None:
            passport = f"{debtor_item.passport_series} {debtor_item.passport_num}"
        else:
            passport = ''

        if debtor_item.pensioner == True:
            pensioner = 'Пенсионер'
        else:
            pensioner = ''

        if debtor_item.birthday is not None:
            try:
                birthday = datetime.strptime(str(debtor_item.birthday), '%Y-%m-%d').strftime("%d.%m.%Y")
            except:
                pass

        result = {
            "creditNum": credit_item.number,
            "creditStatus": status_cd,
            "debtorName": fio,
            "debtorBirthday": birthday,
            "debtorPassport": passport,
            "debtorGrand": pensioner,
            "debtorGender": debtor_item.pol,
            "cessionName": cession_item.name,
            "claimerEP": claimer_ep,
            "cessionDate": cession_item.date,
            "cessionSumma": summa_by_cession,
            "ed_id": ed_id,
            "edType": edType,
            "edNum": edNum,
            "edSumma": edSumma,
            "edSuccession": edSuccession,
            "balanceDebt": balance_debt,
            "summaPayAll": summa_all,
            "summaPayLast": pay_last,
            "datePayLast": date_last,
        }
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }