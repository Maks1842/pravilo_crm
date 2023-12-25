import math
from datetime import date, datetime

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, insert, func, distinct, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor
from src.collection_debt.models import executive_document
from src.legal_work.routers.helper_legal_work import save_case_legal
from src.mail.models import mail_in
from src.references.models import ref_legal_docs, ref_result_statement
from src.collection_debt.routers.executive_document_rout import save_ed
from variables_for_backend import per_page_mov

'''
IncomingMail - извлекаю и добавляю входящую корреспонденцию.
 
Метод автоматически проверяет порядковый номер, дату корреспонденции и очередной номер штрихкода. 
При добавлении новой записи порядковый номер и штрихкод увеличивается на +1, дата корреспонденции = текущей дате.

Структура штрихкода 0100000001 (всего 10 цифр):
01 - признак входящей почты; 00000001 - порядковый номер штрихкода (8 цифр)
'''


# Получить/добавить входящую корреспонденцию
router_incoming_mail = APIRouter(
    prefix="/v1/IncomingMail",
    tags=["Mail"]
)

# date_1: str = None, date_2: str = None,
@router_incoming_mail.get("/")
async def get_incoming_mail(page: int, debtor_id: int = None, dates: List[str] = Query(None, alias="dates[]"),  session: AsyncSession = Depends(get_async_session)):

    per_page = per_page_mov

    try:
        if len(dates) == 1:
            date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
            date_2 = date_1
        else:
            date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
            date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    except:
        date_1 = None
        date_2 = None

    credits_id_query = await session.execute(select(credit.c.id).where(credit.c.debtor_id == debtor_id))
    credits_id_list = credits_id_query.scalars().all()

    try:
        if debtor_id == None and date_1:
            mail_query = await session.execute(select(mail_in).where(and_(mail_in.c.date >= date_1, mail_in.c.date <= date_2)).
                                               order_by(desc(mail_in.c.date)).order_by(desc(mail_in.c.id)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_in.c.id))).filter(and_(mail_in.c.date >= date_1, mail_in.c.date <= date_2)))
        elif debtor_id and date_1 == None:
            mail_query = await session.execute(select(mail_in).where(mail_in.c.credit_id.in_(credits_id_list)).
                                               order_by(desc(mail_in.c.date)).order_by(desc(mail_in.c.id)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_in.c.id))).filter(mail_in.c.credit_id.in_(credits_id_list)))
        elif debtor_id and date_1:
            mail_query = await session.execute(select(mail_in).where(and_(mail_in.c.credit_id.in_(credits_id_list), mail_in.c.date >= date_1, mail_in.c.date <= date_2).
                                                                     order_by(desc(mail_in.c.date)).order_by(desc(mail_in.c.id)).
                                                limit(per_page).offset((page - 1) * per_page)))
            total_mail_query = await session.execute(select(func.count(distinct(mail_in.c.id))).filter(and_(mail_in.c.credit_id.in_(credits_id_list), mail_in.c.date >= date_1, mail_in.c.date <= date_2)))
        else:
            mail_query = await session.execute(select(mail_in).order_by(desc(mail_in.c.date)).order_by(desc(mail_in.c.id)).
                                                limit(per_page).offset((page - 1) * per_page))
            total_mail_query = await session.execute(select(func.count(distinct(mail_in.c.id))))

        total_item = total_mail_query.scalar()
        num_page_all = int(math.ceil(total_item / per_page))

        data_mail = []
        for item in mail_query.mappings().all():

            debtor_fio = ''
            credit_number = ''
            name_doc = ''
            resolution = ''
            ed_id = None
            date_succession = None
            date_entry_force = None
            tribunal_id = None
            name_doc_id = None
            resolution_id = None

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

                ed_query = await session.execute(select(executive_document.c.id,
                                                        executive_document.c.succession,
                                                        executive_document.c.date_entry_force,
                                                        executive_document.c.tribunal_id).where(executive_document.c.credit_id == credit_id).order_by(desc(executive_document.c.id)))
                ed_set = ed_query.mappings().first()

                ed_id = ed_set.id
                if ed_set.succession:
                    date_succession = datetime.strptime(str(ed_set.succession), '%Y-%m-%d').strftime("%d.%m.%Y")
                if ed_set.date_entry_force:
                    date_entry_force = datetime.strptime(str(ed_set.date_entry_force), '%Y-%m-%d').strftime("%d.%m.%Y")
                if ed_set.tribunal_id:
                    tribunal_id = ed_set.tribunal_id

            if item.name_doc_id is not None:
                name_doc_id: int = item.name_doc_id
                name_doc_query = await session.execute(select(ref_legal_docs).where(ref_legal_docs.c.id == name_doc_id))
                name_doc_set = name_doc_query.mappings().one()
                name_doc = name_doc_set.name

            if item.resolution_id is not None:
                resolution_id: int = item.resolution_id
                resolution_query = await session.execute(select(ref_result_statement).where(ref_result_statement.c.id == resolution_id))
                resolution_set = resolution_query.mappings().one()
                resolution = resolution_set.name

            data_mail.append({
                "id": item.id,
                "sequence_num": item.sequence_num,
                "date": datetime.strptime(str(item.date), '%Y-%m-%d').strftime("%d.%m.%Y"),
                "addresser": item.addresser,
                "debtor_fio": debtor_fio,
                "credit_number": credit_number,
                "credit_id": item.credit_id,
                "case_number": item.case_number,
                "legal_doc_name": name_doc,
                "legal_docs_id": name_doc_id,
                "resolution": resolution,
                "resultStatement_id": resolution_id,
                "barcode": item.barcode,
                "comment": item.comment,
                "docDate": None,
                "dateSessionTribunal": None,
                "dateSuccession": date_succession,
                "date_entry_force": date_entry_force,
                "dateStop": '',
                "user_id": None,
                "ed_id": ed_id,
                "tribunal_id": tribunal_id,
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


@router_incoming_mail.post("/")
async def add_incoming_mail(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    mail_list = data_json['data_json']

    result = await save_incoming_mail(mail_list, session)

    return result


async def save_incoming_mail(list_data, session):

    print(f'{list_data=}')

    for data in list_data:
        if data['addresser'] is None:
            return {
                "status": "error",
                "data": None,
                "details": f"Не указано От кого"
            }

        if data['legal_docs_id'] is None:
            return {
                "status": "error",
                "data": None,
                "details": f"Не указано наименование документа"
            }

        if data['date'] is None:
            current_date = date.today()
        else:
            current_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        if data['sequence_num'] is None:
            sequence_num = 1
            barcode = '01' + '00000001'
            try:
                mail_query = await session.execute(select(mail_in).order_by(desc(mail_in.c.sequence_num)))
                mail_set = mail_query.mappings().fetchone()
                sequence_num = mail_set.sequence_num + 1

                if len(mail_set['barcode']) > 0:
                    barcode_split = mail_set['barcode'][2:]
                    barcode_body = str(int(barcode_split) + 1).zfill(8)
                    barcode = f'01{barcode_body}'
            except:
                pass
        else:
            sequence_num = data['sequence_num']
            barcode = data['barcode']

        try:
            data_mail = {
                    "sequence_num": sequence_num,
                    "case_number": data['case_number'],
                    "credit_id": data['credit_id'],
                    "barcode": barcode,
                    "date": current_date,
                    "addresser": data['addresser'],
                    "name_doc_id": data['legal_docs_id'],
                    "resolution_id": data['resultStatement_id'],
                    "comment": data['comment'],
                    }

            if data["id"]:
                mail_id: int = data["id"]
                post_data = update(mail_in).where(mail_in.c.id == mail_id).values(data_mail)
            else:
                post_data = insert(mail_in).values(data_mail)

            await session.execute(post_data)
            await session.commit()
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f"Ошибка при добавлении/изменении Входящей почты. {ex}"
            }

        if data['legalCase_id'] and data['legalCase_id']:
            legal_data = {"date_session_1": datetime.strptime(data['dateSessionTribunal'], '%Y-%m-%d').date(),
                          "credit_id": data['credit_id'],
                          "legal_docs_id": data['legal_docs_id'],}
            await save_case_legal(data['legalCase_id'], data['user_id'], legal_data, session)

        if data['dateSuccession'] and data['ed_id']:
            data_ed = {"succession": datetime.strptime(data['dateSuccession'], '%Y-%m-%d').date()}
            await save_ed(data['ed_id'], data_ed, session)

        if data['date_entry_force'] and data['ed_id']:
            data_ed = {"date_entry_force": datetime.strptime(data['date_entry_force'], '%Y-%m-%d').date()}
            await save_ed(data['ed_id'], data_ed, session)

    return {
        'status': 'success',
        'data': None,
        'details': 'Входящая почта успешно сохранена'
    }