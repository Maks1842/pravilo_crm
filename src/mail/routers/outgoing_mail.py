import math
from datetime import date, datetime

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, insert, func, distinct, update, desc, and_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor
from src.mail.models import mail_out
from src.auth.models import user
from src.routers_helper.data_to_excel.mail_to_excel import mail_out_to_excel
from variables_for_backend import per_page_mov

'''
OutgoingMail - извлекаю и добавляю исходящую корреспонденцию.
 
Метод автоматически проверяет порядковый номер, дату корреспонденции и очередной номер штрихкода. 
При добавлении новой записи порядковый номер и штрихкод увеличивается на +1, дата корреспонденции = текущей дате.

Структура штрихкода 0200000001 (всего 10 цифр):
02 - признак исходящей почты; 00000001 - порядковый номер штрихкода (8 цифр)
'''



# Получить/добавить исходящую корреспонденцию
router_outgoing_mail = APIRouter(
    prefix="/v1/OutgoingMail",
    tags=["Mail"]
)


@router_outgoing_mail.get("/")
async def get_outgoing_mail(page: int, debtor_id: int = None, recipient: str = None, dates: List[str] = Query(None, alias="dates[]"), session: AsyncSession = Depends(get_async_session)):

    per_page = per_page_mov

    if dates and len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1
    elif dates and len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    credits_id_query = await session.execute(select(credit.c.id).where(credit.c.debtor_id == debtor_id))
    credits_id_list = credits_id_query.scalars().all()

    try:
        if debtor_id == None and date_1:
            mail_query = await session.execute(select(mail_out).where(and_(mail_out.c.date >= date_1, mail_out.c.date <= date_2)).
                                               order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_out.c.id))).filter(and_(mail_out.c.date >= date_1, mail_out.c.date <= date_2)))
        elif debtor_id and date_1 == None:
            mail_query = await session.execute(select(mail_out).where(mail_out.c.credit_id.in_(credits_id_list)).
                                               order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_out.c.id))).filter(mail_out.c.credit_id.in_(credits_id_list)))
        elif debtor_id and date_1:
            mail_query = await session.execute(select(mail_out).where(and_(mail_out.c.credit_id.in_(credits_id_list), mail_out.c.date >= date_1, mail_out.c.date <= date_2)).
                                                                     order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                                                     limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_out.c.id))).filter(and_(mail_out.c.credit_id.in_(credits_id_list), mail_out.c.date >= date_1, mail_out.c.date <= date_2)))
        elif recipient and date_1 == None:
            mail_query = await session.execute(select(mail_out).where(mail_out.c.addresser.icontains(recipient)).
                                               order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_out.c.id))).filter(mail_out.c.addresser.icontains(recipient)))
        elif recipient and date_1:
            mail_query = await session.execute(select(mail_out).where(and_(mail_out.c.addresser.icontains(recipient), mail_out.c.date >= date_1, mail_out.c.date <= date_2)).
                                                                      order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                                                      limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_out.c.id))).filter(and_(mail_out.c.addresser.icontains(recipient), mail_out.c.date >= date_1, mail_out.c.date <= date_2)))
        else:
            mail_query = await session.execute(select(mail_out).order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_out.c.id))))

        total_item = total_mail_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_mail = []
        for item in mail_query.mappings().all():

            debtor_fio = None
            credit_number = None
            expenses_mail = 0

            if item.credit_id is not None:
                credit_id: int = item.credit_id
                credits_query = await session.execute(select(credit).where(credit.c.id == credit_id))
                credit_set = credits_query.mappings().one()
                credit_number = credit_set.number
                debtor_id: int = credit_set.debtor_id

                debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
                debtor_item = debtor_query.mappings().one()

                if debtor_item.last_name_2 is not None:
                    debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                                 f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
                else:
                    debtor_fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

                if item.expenses_mail is not None:
                    expenses_mail = item.expenses_mail / 100

            user_query = await session.execute(select(user.c.first_name, user.c.last_name).where(user.c.id == int(item.user_id)))
            user_set = user_query.mappings().fetchone()
            user_name = f'{user_set.first_name} {user_set.last_name or ""}'

            data_mail.append({
                "id": item.id,
                "sequenceNum": item.sequence_num,
                "mailDate": datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y"),
                "barcodeNum": item.barcode,
                "user": user_name,
                "user_id": item.user_id,
                "debtorName": debtor_fio,
                "creditNum": credit_number,
                "credit_id": item.credit_id,
                "caseNum": item.case_number,
                "mailRecipient": item.addresser,
                "addressRecipient": item.recipient_address,
                "docName": item.name_doc,
                "mailMass": item.mass,
                "mailType": item.type_mail,
                "mailCategory": item.category_mail,
                "packageType": item.type_package,
                "symbolNum": item.num_symbol,
                "expensesMail": expenses_mail,
                "trekNum": item.trek,
                "comment": item.comment,
            })

        result = {'data_mail': data_mail,
                  'count_all': total_item,
                  'num_page_all': num_page_all}

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


@router_outgoing_mail.post("/")
async def add_outgoing_mail(new_mail: dict, session: AsyncSession = Depends(get_async_session)):

    result = await save_outgoing_mail(new_mail, session)

    return result


async def save_outgoing_mail(reg_data, session):

    data = reg_data['new_mail']

    if data['mailRecipient'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не указан Получатель"
        }

    if data['docName'] == None:
        return {
            "status": "error",
            "data": None,
            "details": f"Не указано наименование документа"
        }

    if data['mailDate'] == None:
        current_date = date.today()
    else:
        current_date = datetime.strptime(data['mailDate'], '%Y-%m-%d').date()

    if data['sequenceNum'] == None:
        sequence_num = 1
        barcode = '02' + '00000001'
        try:
            mail_query = await session.execute(select(mail_out).order_by(desc(mail_out.c.sequence_num)))
            mail_set = mail_query.mappings().fetchone()
            sequence_num = mail_set.sequence_num + 1

            if len(mail_set.barcode) > 0:
                barcode_split = mail_set.barcode[2:]
                barcode_body = str(int(barcode_split) + 1).zfill(8)
                barcode = f'02{barcode_body}'
        except:
            pass
    else:
        sequence_num = data['sequenceNum']
        barcode = data['barcodeNum']

    if data['expensesMail'] is not None:
        expenses_mail = int(float(data['expensesMail']) * 100)
    else:
        expenses_mail = None

    try:
        data_mail = {
            "sequence_num": sequence_num,
            "case_number": data['caseNum'],
            "credit_id": data['credit_id'],
            "date": current_date,
            "name_doc": data['docName'],
            "addresser": data['mailRecipient'],
            "recipient_address": data['addressRecipient'],
            "mass": int(data['mailMass']),
            "expenses_mail": expenses_mail,
            "trek": data['trekNum'],
            "category_mail": data['mailCategory'],
            "type_mail": data['mailType'],
            "type_package": data['packageType'],
            "barcode": barcode,
            "num_symbol": data['symbolNum'],
            "user_id": data['user_id'],
            "comment": data['comment'],
        }

        await save_mail_out(data["id"], data_mail, session)

    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении Исходящей почты. {ex}"
        }

    return {
        'status': 'success',
        'data': None,
        'details': 'Исходящая почта успешно сохранена'
    }


async def save_mail_out(mail_id, data, session):
    if mail_id:
        post_data = update(mail_out).where(mail_out.c.id == int(mail_id)).values(data)
    else:
        post_data = insert(mail_out).values(data)

    await session.execute(post_data)
    await session.commit()



# Получить порядковый номер Mail_out
router_mail_number = APIRouter(
    prefix="/v1/GetMailNumber",
    tags=["Mail"]
)


@router_mail_number.get("/")
async def get_mail_number(fragment, session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(mail_out).where(cast(mail_out.c.sequence_num, String).contains(str(fragment))))

        result = []
        for item in query.mappings().all():

            result.append({
                "mail_id": item['id'],
                "mail_number": item['sequence_num'],
            })
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }




# Создает почтовый реестр Excel
router_mail_to_excel = APIRouter(
    prefix="/v1/MailToExcel",
    tags=["Mail"]
)


@router_mail_to_excel.post("/")
def mail_to_excel(data_json: dict):

    result = mail_out_to_excel(data_json)

    return result