import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor
from src.mail.models import mail_out
from src.auth.models import user

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
async def get_outgoing_mail(page: int, debtor_id: int = None, recipient: int = None, dates1: str = None, dates2: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20

    if dates2 is None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    credits_id_query = await session.execute(select(credit.c.id).where(credit.c.debtor_id == debtor_id))
    credits_id_list = credits_id_query.scalars().all()

    try:
        if debtor_id == None and dates1:
            mail_query = await session.execute(select(mail_out).where(and_(mail_out.c.date >= dates1, mail_out.c.date <= dates2)).
                                               order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(mail_out.c.date == dates1)))
        elif debtor_id and dates1 == None:
            mail_query = await session.execute(select(mail_out).where(mail_out.c.credit_id.in_(credits_id_list)).
                                               order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(mail_out.c.credit_id.in_(credits_id_list))))
        elif debtor_id and dates1:
            mail_query = await session.execute(select(mail_out).where(and_(mail_out.c.credit_id.in_(credits_id_list), mail_out.c.date >= dates1, mail_out.c.date <= dates2).
                                                                     order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                                                     limit(per_page).offset((page - 1) * per_page)))
            total_item_query = await session.execute(func.count(distinct(and_(mail_out.c.credit_id.in_(credits_id_list), mail_out.c.date >= dates1, mail_out.c.date <= dates2))))
        elif recipient and dates1 == None:
            mail_query = await session.execute(select(mail_out).where(mail_out.c.addresser.icontains(recipient)).
                                               order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(mail_out.c.addresser.icontains(recipient))))
        elif recipient and dates1:
            mail_query = await session.execute(select(mail_out).where(and_(mail_out.c.addresser.icontains(recipient), mail_out.c.date >= dates1, mail_out.c.date <= dates2).
                                                                      order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                                                      limit(per_page).offset((page - 1) * per_page)))
            total_item_query = await session.execute(func.count(distinct(and_(mail_out.c.addresser.icontains(recipient), mail_out.c.date >= dates1, mail_out.c.date <= dates2))))
        else:
            mail_query = await session.execute(select(mail_out).order_by(desc(mail_out.c.date)).order_by(desc(mail_out.c.id)).
                                               limit(per_page).offset((page - 1) * per_page))
            total_item_query = await session.execute(func.count(distinct(mail_out.c.id)))

        total_item = total_item_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_mail = []
        for item in mail_query.mappings().all():

            debtor_fio = ''
            credit_number = ''

            if item['credit_id'] is not None and item['credit_id'] != '':
                credit_id: int = item['credit_id']
                credits_query = await session.execute(select(credit).where(credit.c.id == credit_id))
                credit_set = credits_query.mappings().one()
                credit_number = credit_set['number']
                debtor_id: int = credit_set['debtor_id']

                debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
                debtor_item = debtor_query.mappings().one()

                if debtor_item['last_name_2'] is not None and debtor_item['last_name_2'] != '':
                    debtor_fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}" \
                                 f" ({debtor_item['last_name_2']} {debtor_item['first_name_2']} {debtor_item['second_name_2'] or ''})"
                else:
                    debtor_fio = f"{debtor_item['last_name_1']} {debtor_item['first_name_1']} {debtor_item['second_name_1'] or ''}"

            user_query = await session.execute(select(user.c.first_name, user.c.last_name).where(user.c.id == int(item['user_id'])))
            user_set = user_query.mappings().fetchone()
            user_name = f'{user_set["first_name"]} {user_set["last_name"] or ""}'

            data_mail.append({
                "id": item['id'],
                "sequenceNum": item['sequence_num'],
                "mailDate": item['date'],
                "barcodeNum": item['barcode'],
                "user": user_name,
                "user_id": item['user_id'],
                "debtorName": debtor_fio,
                "creditNum": credit_number,
                "credit_id": item['credit_id'],
                "caseNum": item['case_number'],
                "mailRecipient": item['addresser'],
                "addressRecipient": item['recipient_address'],
                "docName": item['name_doc'],
                "mailMass": item['mass'],
                "mailType": item['type_mail'],
                "mailCategory": item['category_mail'],
                "packageType": item['type_package'],
                "symbolNum": item['num_symbol'],
                "stateDuty": item['gov_toll'],
                "trekNum": item['trek'],
                "comment": item['comment'],
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
            sequence_num = mail_set['sequence_num'] + 1

            if len(mail_set['barcodeNum']) > 0:
                barcode_split = mail_set['barcodeNum'][2:]
                barcode_body = str(int(barcode_split) + 1).zfill(8)
                barcode = f'02{barcode_body}'
        except:
            pass
    else:
        sequence_num = data['sequenceNum']
        barcode = data['barcodeNum']

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
            "gov_toll": data['stateDuty'],
            "trek": data['trekNum'],
            "category_mail": data['mailCategory'],
            "type_mail": data['mailType'],
            "type_package": data['packageType'],
            "barcode": barcode,
            "num_symbol": data['symbolNum'],
            "user_id": data['user_id'],
            "comment": data['comment'],
        }

        if data["id"]:
            mail_id: int = data["id"]
            post_data = update(mail_out).where(mail_out.c.id == mail_id).values(data_mail)
        else:
            post_data = insert(mail_out).values(data_mail)

        await session.execute(post_data)
        await session.commit()
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