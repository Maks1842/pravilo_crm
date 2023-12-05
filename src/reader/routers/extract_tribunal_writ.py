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
from src.store_value import section_card_id_tribun

'''
Метод извлечения Судебных приказов
!!! Импортированный файл должен быть формата .pdf, с возможностью редактирования
'''


router_extract_tribunal_writ = APIRouter(
    prefix="/v1/TribunalWritExtractPDF",
    tags=["Reader"]
)


@router_extract_tribunal_writ.post("/")
async def extract_tribunal_writ(files: List[UploadFile] = File(...), session: AsyncSession = Depends(get_async_session)):

    type_doc = 'СП'
    re_pattern = RePattern.heading_sp

    path_result = f'{path_main}/src/media/reader/result'
    current_date = datetime.now() + timedelta(hours=3)
    directory_result = f'{path_result}/{type_doc}_{current_date.strftime("%d.%m.%Y_%H.%M.%S")}'
    os.mkdir(directory_result)

    count = 1
    data_items = []
    count_items = 0

    for item_file in files:

        with open(f'{path_main}/src/media/reader/tribunal_writ_scan_{count}.pdf', 'wb+') as f:
            for chunk in item_file.file:
                f.write(chunk)

        path_file = f'{path_main}/src/media/reader/tribunal_writ_scan_{count}.pdf'

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
            "section_card_id": section_card_id_tribun,
            "credit_id": credit_id,
            "creditNum": f'{fio}, {credit_num}',
            "legal_section_id": legal_section_id,
            "legal_section": legal_section_name,
            "legal_docs_id": legal_docs_id,
            "legal_docs": item['type_doc'],
            "dublED": item['type_doc_dubl'],
            "dateED": date_doc,
            "numCase": item['num_doc'],
            "tribunalName": item['tribunal'],
            "debtorName": item['name_debtor'],
            "debtorBirthday": item['birthday'],
            "creditor": item['name_creditor'],
            "numCredit": item['num_kd'],
            "summaDebt": item['summa_debt'],
            "stateDuty": item['summa_duty'],
            "file_name": item['file_name'],
            "path": item['directory_result'],
            "date_entry_force": None,
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
        name_file_dubl = ''
        count_doc += 1

        # Исходный и обработанный текст, весь
        result_convert = convert_pdf_to_string(file, directory_result)
        text = re.sub('\n', ' ', result_convert[0])
        page_count = result_convert[1].page_count

        text_type = re.search(RePattern.text_type, str(text)).group()
        text_tribun = re.search(RePattern.text_tribun, str(text)).group()
        try:
            text_debtor = re.search(RePattern.text_debt_sp, str(text)).group()
        except:
            text_debtor = ''
        try:
            text_creditor = re.search(RePattern.text_credit, str(text)).group()
        except:
            text_creditor = ''
        try:
            text_debt = re.search(RePattern.text_debt1, str(text)).group()
        except:
            text_debt = ''
        try:
            text_duty = re.search(RePattern.text_duty1, str(text_creditor)).group()
        except:
            text_duty = ''

        current_date = date.today()
        date_today = current_date.strftime("%d.%m.%Y")
        year_today = re.search(r'\d{4}', date_today).group()
        months = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
                  'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}

        # Тип документа
        type_doc = 'Судебный приказ'

        # Определяю "Дубликат" или нет
        try:
            type_doc_dubl = re.search(RePattern.heading_dubl, str(text)).group()
            if re.findall(r'(?i)(д\s*у\s*б\s*л\s*и\s*к\s*а\s*т)', re.search(RePattern.heading_dubl, str(text)).group()):
                name_file_dubl = 'Д'
        except:
            type_doc_dubl = ''
            name_file_dubl = ''

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

        # Номер документа
        try:
            num_doc = re.sub(r'(?i)[а-я\s]+', '', re.search(RePattern.num_doc1, str(text_type)).group())
        except:
            num_doc = 'ОШИБКА'

        # Суд выдавший документ
        try:
            tribunal = re.search(RePattern.tribun3, str(text_tribun)).group()
            if len(tribunal) > 200:
                tribunal = tribunal[:200]
        except:
            try:
                tribunal = re.search(RePattern.tribun2, str(text_tribun)).group()
            except:
                tribunal = 'ОШИБКА'

        # Имя должника
        try:
            name_debt = re.search(RePattern.name_debt_res, str(text_debtor)).group()
        except:
            name_debt = 'ОШИБКА'
        name_list_debt = re.findall(r'\w+', name_debt)

        # Дата рождения должника
        try:
            if re.findall(r'[а-я]', re.search(RePattern.birthday1, str(text)).group()):
                birthday_date = re.search(RePattern.birthday1, str(text)).group()
                text_date = re.sub(r'[\s»]+', '', birthday_date)
                month = re.search(r'\D+', text_date).group()
                birthday = re.sub(r'\D+', '.' + months[month] + '.', text_date)
            else:
                birthday = re.search(RePattern.birthday1, str(text)).group()
        except:
            birthday = 'ОШИБКА'

        # Имя кредитора
        try:
            name_cred = re.search(RePattern.name_cred, str(text_creditor)).group()
        except:
            name_cred = 'ОШИБКА'
        name_list_creditor = re.findall(r'\w+', name_cred)

        # Номер КД
        try:
            num_kd = re.sub(r'[\s№]+', '', re.search(RePattern.num_kd2, str(text_creditor)).group())
            name_file_num_kd = re.sub(r'[\/\\\<\>\*\:\?\|]+', '_', num_kd)
            if num_kd == '':
                num_kd = 'ОШИБКА'
                name_file_num_kd = f'ОШИБКА_файла_{count_doc}'
        except:
            num_kd = 'ОШИБКА'
            name_file_num_kd = f'ОШИБКА_файла_{count_doc}'

        # Сумма долга
        try:
            summa_debt_re = re.sub(r'\s+', '', re.search(RePattern.summa_rub, str(text_debt)).group())
            summa_debt = re.sub(r',', '.', summa_debt_re)
        except:
            try:
                summa_debt_re = re.sub(r'\s+', '', re.sub(r'\s*\([\D\s]*|\s*руб\.\s*|\s*рубля\s*', ',', re.search(RePattern.summa_rub2, str(text_debt)).group()))
                summa_debt = re.sub(r',', '.', summa_debt_re)
            except:
                summa_debt = 'ОШИБКА'

        # Сумма пошлины
        try:
            summa_duty_re = re.sub(r'\s+', '', re.search(RePattern.summ_duty1, str(text_duty)).group())
            summa_duty = re.sub(r',', '.', summa_duty_re)
        except:
            try:
                summa_duty_re = re.sub(r'\s+', '', re.sub(r'\s*\([\D\s]*|\s*руб\.\s*|\s*руб\s*|\s*рубля\s*', ',', re.search(RePattern.summ_duty2, str(text_duty)).group()))
                summa_duty = re.sub(r',', '.', summa_duty_re)
            except:
                summa_duty = 'ОШИБКА'

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

        # Меняю окончание ФИО взыскателя
        try:
            name_cd = []
            for name1 in name_list_creditor:
                if re.findall(r'(а)$', name1) == list('а'):
                    name_cd.append(''.join(re.sub(r'(а)$', '', name1)))
                else:
                    name_cd.append(name1)
            name_creditor1 = 'None'
            count = 0
            for i in name_cd:
                count += 1
                if count == 1:
                    name_creditor1 = str(i)
                elif count > 1:
                    name_creditor1 = str(name_creditor1) + ' ' + str(i)
            name_creditor = (name_creditor1)
        except:
            name_creditor = 'ОШИБКА'

        # Обработанный файл переименовывается в соответствии с извлеченной информацией
        result_convert[1].close()
        file_oldname = os.path.join(f'{directory_result}/{file}')

        file_newname = os.path.join(f'{directory_result}/', f'{type_doc_file}_{name_file_dubl}_{name_file_num_kd}_{page_count}.pdf')

        os.rename(file_oldname, file_newname)
        base_name = os.path.basename(file_newname)

        result.append({
            'type_doc': type_doc,
            'type_doc_dubl': type_doc_dubl,
            'date_doc': date_doc,
            'num_doc': num_doc,
            'tribunal': tribunal,
            'name_debtor': name_debtor,
            'birthday': birthday,
            'name_creditor': name_creditor,
            'num_kd': num_kd,
            'summa_debt': summa_debt,
            'summa_duty': summa_duty,
            'file_name': base_name,
            'directory_result': directory_result,
        })

    return result