"""
ДЛЯ деления общего файла PDF отдельные документы
Скрипт находит указанный текст в документе pdf и указывает номер страницы
"""
import os
import fitz
import re
from datetime import datetime, timedelta
from src.config import path_main

# Определяю номера страниц по наличию заданного текста
def numbers_page(file, re_pattern):
    with open(file, 'rb') as f:
        doc_pdf = fitz.open(f)
        page_all = len(doc_pdf)

    numbers_page = []
    for current_page in range(page_all):
        page = doc_pdf.load_page(current_page)
        text_page = doc_pdf.get_page_text(current_page)
        try:
            text_search = re.search(re_pattern, str(text_page)).group()
            if page.search_for(text_search):
                numbers_page.append(current_page)
        except:
            pass

    return numbers_page


def split_into_pages(type_doc, path_file, re_pattern, directory_result):
    # path_result = f'{path_main}/src/media/reader/result'
    list_page = numbers_page(path_file, re_pattern)

    if len(list_page) == 0:
        return 'Error'

    current_date = datetime.now() + timedelta(hours=3)
    # directory_result = f'{path_result}/{type_doc}_{current_date.strftime("%d.%m.%Y_%H.%M.%S")}'
    # os.mkdir(directory_result)

    count = 0
    count_doc = 0
    for page in list_page:
        with open(path_file, 'rb') as f:
            doc_pdf = (fitz.Document(f))
            page_end = (len(doc_pdf))
            count += 1
        try:
            # Указываю с какой по какую страницу извлекать
            pages_list = range(page, list_page[count])

            # Извлекать заданные страницы
            doc_pdf.select(pages_list)
        except:
            pages_list = range(page, page_end)
            doc_pdf.select(pages_list)

        count_doc += 1

        # garbage=2 - удаляет мусор из .pdf. Читать доку https://pymupdf.readthedocs.io/en/latest/document.html#Document.save
        doc_pdf.save(f'{directory_result}/{str(count_doc)}_{current_date.strftime("%d.%m.%Y")}.pdf', garbage=2)

    return

# split_into_pages()
# numbers_page()