import re
import os
from os import listdir
import fitz
from datetime import datetime, date, timedelta

from typing import List
from fastapi import APIRouter, UploadFile, Depends, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor
from src.config import path_main
from src.reader.routers.re_pattern import RePattern
from src.reader.routers.split_docs_pdf import split_into_pages
from src.references.models import ref_legal_section, ref_legal_docs

'''
Метод извлечения Судебных Решений
!!! Импортированный файл должен быть формата .pdf, с возможностью редактирования
'''


router_extract_decision = APIRouter(
    prefix="/v1/DecisionExtractPDF",
    tags=["Reader"]
)


@router_extract_decision.post("/")
async def extract_decision(files: List[UploadFile] = File(...), session: AsyncSession = Depends(get_async_session)):

    type_doc = 'РШН'
    re_pattern = RePattern.heading_dec

    path_result = f'{path_main}/src/media/reader/result'
    current_date = datetime.now() + timedelta(hours=3)
    directory_result = f'{path_result}/{type_doc}_{current_date.strftime("%d.%m.%Y_%H.%M.%S")}'
    os.mkdir(directory_result)

    count = 1
    data_items = []
    count_items = 0

    for item_file in files:

        with open(f'{path_main}/src/media/reader/data/docs_scan_{count}.pdf', 'wb+') as f:
            for chunk in item_file.file:
                f.write(chunk)

        path_file = f'{path_main}/src/media/reader/data/docs_scan_{count}.pdf'

        split_into_pages(path_file, re_pattern, directory_result, count)

        count += 1

    extract_items = data_executing_doc(type_doc, directory_result)

    for item in extract_items:
        credit_id = None
        credit_num = ''
        legal_section_name = None
        legal_docs_id = None
        legal_section_id = None
        fio = 'Не определен'
        count_items += 1

        credits_query = await session.execute(select(credit).where(credit.c.number == item['num_kd']))
        credit_set = credits_query.mappings().fetchone()

        if credit_set:
            credit_id = credit_set.id
            credit_num = credit_set.number
            debtor_id: int = credit_set.debtor_id

            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()

            if debtor_item.last_name_2 is not None:
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                             f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

        if re.findall(r'\d{2}\.\d{2}\.\d{4}', item['date_doc']):
            try:
                date_doc = datetime.strptime(item['date_doc'], '%d.%m.%Y').strftime("%Y-%m-%d")
            except:
                date_doc = None
        else:
            date_doc = item['date_doc']

        legal_docs_query = await session.execute(select(ref_legal_docs).where(ref_legal_docs.c.name == item['type_doc']))
        legal_docs_answ = legal_docs_query.mappings().fetchone()

        if legal_docs_answ:
            legal_docs_id = legal_docs_answ.id
            legal_section_id = legal_docs_answ.legal_section_id

        if legal_section_id:
            legal_section_query = await session.execute(select(ref_legal_section.c.name).where(ref_legal_section.c.id == int(legal_section_id)))
            legal_section_answ = legal_section_query.mappings().fetchone()

            if legal_section_answ:
                legal_section_name = legal_section_answ.name

        data_items.append({
            "credit_id": credit_id,
            "creditNum": f'{fio}, {credit_num}',
            "legal_section_id": legal_section_id,
            "legal_section": legal_section_name,
            "legal_docs_id": legal_docs_id,
            "legal_docs": item['type_doc'],
            "dateED": date_doc,
            "tribunalName": item['tribunal'],
            "debtorName": item['name_debtor'],
            "numCase": item['num_ep'],
            "numCredit": item['num_kd'],
            "resultStatement": item['resolution'],
            "file_name": item['file_name'],
            "path": item['directory_result'],
            "tribunal_id": None,
        })

    result = {'data_items': data_items,
              'count_all': count_items}

    return result


# 2 шаг Извлекаю весь текст из pdf
def convert_pdf_to_string(file, directory_result):
    text_list = []
    with open(f'{directory_result}/{file}', 'rb') as f:
        doc_pdf = fitz.open(f)
        for current_page in range(len(doc_pdf)):
            text_page = doc_pdf.get_page_text(current_page)
            text_list.append(text_page)
            text = ''.join(text_list)
    return text, doc_pdf


# 1 шаг Перебираю все файлы из папки для проверки
def data_executing_doc(type_doc_file, directory_result):

    count_doc = 0
    filelist = listdir(directory_result)

    result = []
    for file in filelist:
        count_doc += 1

        # Исходный и обработанный текст, весь
        result_convert = convert_pdf_to_string(file, directory_result)
        text = re.sub('\n', ' ', result_convert[0])
        page_count = result_convert[1].page_count

        text_type = re.search(RePattern.text_type, str(text)).group()

        current_date = date.today()
        date_today = current_date.strftime("%d.%m.%Y")
        year_today = re.search(r'\d{4}', date_today).group()
        months = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
                  'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}

        # Тип документа
        type_doc = 'Решение'

        # Дата документа. Дополнительный фильтр на возраст документа
        try:
            if re.findall(r'[а-я]', re.search(RePattern.date_doc1, str(text)).group()):
                date_doc1 = re.search(RePattern.date_doc1, str(text)).group()
                text_date = re.sub(r'[\s»]+', '', date_doc1)
                month = re.search(r'\D+', text_date).group()
                date1_doc = re.sub(r'\D+', '.' + months[month] + '.', text_date)
                year_old = re.search(r'\d{4}', str(date1_doc)).group()
                if int(year_today) - int(year_old) < 11:
                    date_doc = re.sub(r'\D+', '.' + months[month] + '.', text_date)
                else:
                    date_doc = 'ОШИБКА'
            else:
                date1_doc = re.search(RePattern.date_doc1, str(text)).group()
                year_old = re.search(r'\d{4}', str(date1_doc)).group()
                if int(year_today) - int(year_old) < 11:
                    date_doc = re.search(RePattern.date_doc1, str(text)).group()
                else:
                    date_doc = 'ОШИБКА'
        except:
            date_doc = 'ОШИБКА'

        # Суд выдавший документ
        try:
            tribunal = re.search(RePattern.tribun3, str(text_type)).group()
            if len(tribunal) > 200:
                tribunal = tribunal[:200]
        except:
            tribunal = 'ОШИБКА'

        # Имя должника
        try:
            name_debt = re.search(RePattern.name_debt_opr, str(text)).group()
        except:
            name_debt = 'ОШИБКА'
        name_list_debt = re.findall(r'\w+', name_debt)

        # Тип заявления
        try:
            statement_type = re.search(RePattern.statement_type_dec, str(text)).group()
        except:
            statement_type = 'ОШИБКА'

        # Номер ИП
        try:
            num_ep = re.sub(r'\\', '/', re.search(RePattern.num_ip, str(text)).group())
        except:
            num_ep = 'ОШИБКА'

        # Номер КД
        try:
            num_kd = re.sub(r'(?i)[№:\s]+', '', re.search(RePattern.num_kd2, str(text)).group())
            name_file_num_kd = re.sub(r'[\/\\\<\>\*\:\?\|]+', '_', num_kd)
            if num_kd == '':
                num_kd = 'ОШИБКА'
                name_file_num_kd = f'ОШИБКА_файла_{count_doc}'
        except:
            num_kd = 'ОШИБКА'
            name_file_num_kd = f'ОШИБКА_файла_{count_doc}'

        # Резолюция
        try:
            resolution = re.search(RePattern.resolution, str(text)).group()
        except:
            resolution = 'ОШИБКА'

        # Меняю окончание ФИО должника
        try:
            name_db = []
            count = 0
            for name1 in name_list_debt:
                if count < 3:
                    if re.findall(r'(ой|ы|и|е)$', name1):
                        name_db.append(''.join(re.sub(r'(ой|ы|и|е)$', 'а', name1)))
                    elif re.findall(r'(а|у)$', name1):
                        name_db.append(''.join(re.sub(r'(а|у)$', '', name1)))
                    elif re.findall(r'(я|ю)$', name1):
                        name_db.append(''.join(re.sub(r'(я|ю)$', 'й', name1)))
                    else:
                        name_db.append(name1)
                    count += 1
                else:
                    name_db.append(name1)
            name_debtor1 = 'None'
            name_debtor2 = name_db[0] + ' ' + str(re.sub(r'(?<=\w)\w+', '.', name_db[1])) + ' ' + str(
                re.sub(r'(?<=\w)\w+', '.', name_db[2]))
            name_file_debtor = (name_debtor2)
            count = 0
            for i in name_db:
                count += 1
                if count == 1:
                    name_debtor1 = str(i)
                elif count > 1:
                    name_debtor1 = str(name_debtor1) + ' ' + str(i)
            name_debtor = (name_debtor1)
        except:
            name_debtor = 'ОШИБКА'
            name_file_debtor = 'ОШИБКА'

        # Обработанный файл переименовывается в соответствии с извлеченной информацией
        result_convert[1].close()
        file_oldname = os.path.join(f'{directory_result}/{file}')

        file_newname = os.path.join(f'{directory_result}/', f'{type_doc_file}_{name_file_num_kd}_{statement_type} от {date_doc}_{name_file_debtor}_{page_count}.pdf')

        os.rename(file_oldname, file_newname)
        base_name = os.path.basename(file_newname)

        result.append({
            'type_doc': type_doc,
            'date_doc': date_doc,
            'tribunal': tribunal,
            'name_debtor': name_debtor,
            'statement_type': statement_type,
            'num_ep': num_ep,
            'num_kd': num_kd,
            'resolution': resolution,
            'file_name': base_name,
            'directory_result': directory_result,
        })

    return result