import re

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, credit, debtor
from src.references.models import ref_status_credit, ref_type_ed
from src.debts.schemas import CessionCreate, CreditCreate
from src.payments.models import payment
from src.collection_debt.models import executive_document, executive_productions


# Получить/добавить цессию
router_cession = APIRouter(
    prefix="/v1/Cession",
    tags=["Debts"]
)


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
        result = []
        for item in answer.all():
            data = dict(item._mapping)

            if data['summa'] is not None and data['summa'] != '':
                summa = data['summa'] / 100
            else:
                summa = 0

            result.append({
                "id": data['id'],
                "name": data['name'],
                "number": data['number'],
                "date": data['date'],
                "summa": summa,
                "cedent": data['cedent'],
                "cessionari": data['cessionari'],
                "date_old_cession": data['date_old_cession']
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_cession.post("/")
async def add_cession(new_cession: CessionCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_cession.model_dump()

    try:
        summa = req_data["summa"] * 100

        data = {
            "name": req_data["name"],
            "number": req_data["number"],
            "date": req_data["date"],
            "summa": summa,
            "cedent": req_data["cedent"],
            "cessionari": req_data["cessionari"],
            "date_old_cession": req_data['date_old_cession'],
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
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "cession_name": item_dic['name'],
                "value": {
                    "cession_id": item_dic["id"],
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

            if data['summa'] is not None and data['summa'] != '':
                summa = data['summa'] / 100
            else:
                summa = 0

            if data['summa_by_cession'] is not None and data['summa_by_cession'] != '':
                summa_by_cession = data['summa_by_cession'] / 100
            else:
                summa_by_cession = 0

            if data['percent_of_od'] is not None and data['percent_of_od'] != '':
                percent_of_od = data['percent_of_od'] / 100
            else:
                percent_of_od = 0

            if data['overdue_od'] is not None and data['overdue_od'] != '':
                overdue_od = data['overdue_od'] / 100
            else:
                overdue_od = 0

            if data['overdue_percent'] is not None and data['overdue_percent'] != '':
                overdue_percent = data['overdue_percent'] / 100
            else:
                overdue_percent = 0

            if data['penalty'] is not None and data['penalty'] != '':
                penalty = data['penalty'] / 100
            else:
                penalty = 0

            if data['gov_toll'] is not None and data['gov_toll'] != '':
                gov_toll = data['gov_toll'] / 100
            else:
                gov_toll = 0

            if data['balance_debt'] is not None and data['balance_debt'] != '':
                balance_debt = data['balance_debt'] / 100
            else:
                balance_debt = 0

            result.append({
                'id': data['id'],
                'debtor_id': data['debtor_id'],
                'status_cd': status,
                'status_cd_id': data['status_cd_id'],
                'creditor': data['creditor'],
                'number': data['number'],
                'date_start': data['date_start'],
                'date_end': data['date_end'],
                'summa': summa,
                'summa_by_cession': summa_by_cession,
                'interest_rate': data['interest_rate'],
                'percent_of_od': percent_of_od,
                'overdue_od': overdue_od,
                'overdue_percent': overdue_percent,
                'penalty': penalty,
                'gov_toll': gov_toll,
                'cession_id': data['cession_id'],
                'balance_debt': balance_debt,
                'credits_old': data['credits_old'],
                'comment': data['comment'],
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_credits.post("/")
async def add_credits(new_credit: CreditCreate, session: AsyncSession = Depends(get_async_session)):

    req_data = new_credit.model_dump()

    summa = req_data["summa"] * 100
    summa_by_cession = req_data["summa_by_cession"] * 100
    overdue_od = req_data["overdue_od"] * 100
    overdue_percent = req_data["overdue_percent"] * 100
    penalty = req_data["penalty"] * 100
    percent_of_od = req_data["percent_of_od"] * 100
    gov_toll = req_data["gov_toll"] * 100
    balance_debt = req_data["balance_debt"] * 100

    try:
        data = {
            "creditor": req_data["creditor"],
            "number": req_data["number"],
            "date_start": req_data["date_start"],
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

    try:
        credit_query = await session.execute(select(credit).where(credit.c.id == credit_id))
        credit_item = dict(credit_query.one()._mapping)

        if credit_item['balance_debt'] is not None and credit_item['balance_debt'] != '':
            balance_debt = credit_item['balance_debt'] / 100
        else:
            balance_debt = 0

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item['debtor_id'])))
        debtor_item = dict(debtor_query.one()._mapping)

        cession_query = await session.execute(select(cession).where(cession.c.id == int(credit_item['cession_id'])))
        cession_item = dict(cession_query.one()._mapping)

        status_cd_query = await session.execute(select(ref_status_credit).where(ref_status_credit.c.id == int(credit_item['status_cd_id'])))
        status_cd_item = dict(status_cd_query.one()._mapping)
        status_cd = status_cd_item['name']

        try:
            summa_query = await session.execute(select(func.sum(payment.c.summa)).where(payment.c.credit_id == credit_id))
            summa_all = summa_query.scalar() / 100

            pay_query = await session.execute(select(payment).where(payment.c.credit_id == credit_id).order_by(desc(payment.c.id)))
            payment_set = dict(pay_query.first()._mapping)
            pay_last = payment_set['summa'] / 100
            date_last = payment_set['date']
        except:
            summa_all = 0
            pay_last = 0
            date_last = ''

        try:
            ed_query = await session.execute(select(executive_document).where(executive_document.c.credit_id == credit_id).order_by(desc(executive_document.c.id)))
            ed_set = dict(ed_query.first()._mapping)

            ed_type_query = await session.execute(select(ref_type_ed.c.name).where(ref_type_ed.c.id == int(ed_set['type_ed_id'])))
            ed_type = ed_type_query.scalar()
            ed_id = ed_set['id']
            edType = ed_type
            edNum = ed_set['number']
            edSumma = ed_set['summa_debt_decision'] / 100
            edSuccession = ed_set['succession']
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

        if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
            fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                  f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
        else:
            fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

        if debtor_item['passport_series'] is not None and debtor_item['passport_series'] != '':
            passport = f"{debtor_item['passport_series']} {debtor_item['passport_num']}"
        else:
            passport = ''

        if debtor_item['pensioner'] == True:
            pensioner = 'Пенсионер'
        else:
            pensioner = ''

        result = {
            "creditNum": credit_item['number'],
            "creditStatus": status_cd,
            "debtorName": fio,
            "debtorBirthday": debtor_item['birthday'],
            "debtorPassport": passport,
            "debtorGrand": pensioner,
            "debtorGender": debtor_item['pol'],
            "cessionName": cession_item['name'],
            "claimerEP": claimer_ep,
            "cessionDate": cession_item['date'],
            "cessionSumma": credit_item['summa_by_cession'],
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