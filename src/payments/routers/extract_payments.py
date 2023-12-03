import re
import openpyxl
import pandas as pd
from fastapi import APIRouter, UploadFile
from src.config import path_main
from src.payments.routers.re_pattern_pay import RePattern


'''
Метод извлечения платежей из банковских выписок Excel
'''
router_extract_payments = APIRouter(
    prefix="/v1/ExtractPaymentsExcel",
    tags=["Payments"]
)


@router_extract_payments.post("/")
async def extract_payments(file_object: UploadFile):

    with open(f'{path_main}/src/media/data/bank_records_file.xlsx', 'wb+') as f:
        for chunk in file_object.file:
            f.write(chunk)

    path_file = f'{path_main}/src/media/data/bank_records_file.xlsx'

    extract_payments_list = payment_reader_xlsx(path_file)

    data_payment = []
    summa_pay = 0
    count_pay = 0

    for pay in extract_payments_list:
        credit_id = None
        credit_num = 'Отсутствует'
        count_pay += 1
        summa_pay += pay['payment']

        fio_split = pay['fio'].split()

        data_payment.append({
            "credit_id": credit_id,
            "creditNum": credit_num,
            "debtorName": pay['fio'],
            "numEP": pay['ep'],
            "numED": pay['ed'],
            "summa": pay['payment'] / 100,
            "date": pay['date'],
            "numPayDoc": pay['num_pay'],
            "departmentPay": pay['department'],
        })

    result = {'data_payment': data_payment,
              'summa_all': summa_pay / 100,
              'count_all': count_pay}

    return result


def payment_reader_xlsx(path_file):

    book = openpyxl.load_workbook(path_file)
    sheet = book.active

    for row in range(1, sheet.max_row):
        for cell in range(0, sheet.max_column):
            if re.findall(r'(?i)турбозайм', str(sheet[row][cell].value)):
                result = refund_payments_from_cedent(sheet)

                return result


def refund_payments_from_cedent(sheet):
    payments = []

    col_result = 0
    col_debit = 0
    col_summa = 0
    date_pay = None
    department = 'Возврат платежей от Цедента'
    for row in range(1, sheet.max_row):
        for cell in range(0, sheet.max_column):

            if re.findall(r'(?i)итого', str(sheet[row][cell].value)):
                col_result = cell
            if re.findall(r'по\s+дебету', str(sheet[row][cell].value)):
                col_debit = cell
            if re.findall(r'в\s+рублях', str(sheet[row][cell].value)):
                col_summa = cell
            if re.findall(r'(?i)Дата\s+операционного\s+дня', str(sheet[row][cell].value)):
                date_pay = re.search(r'\d{2}\.\d{2}\.\d{4}', str(sheet[row][cell].value)).group()

        # Если столбец "Поступление" содержит данные, то парсинг строки
        if re.findall(r'(?i)итого', str(sheet[row][col_result].value)):
            return payments

        elif re.findall(RePattern.payment_memori, str(sheet[row][col_summa].value)):
            payment_text = sheet[row][col_summa].value
            try:
                payment_format = re.sub(r'-', '.', payment_text)
            except:
                payment_format = payment_text
            payment = int(float(payment_format) * 100)

            debtor = re.search(RePattern.pay_fio_memori, str(sheet[row][col_debit].value)).group()

            payments.append({"fio": debtor,
                             "ep": None,
                             "ed": None,
                             "il": None,
                             "date": date_pay,
                             "payment": payment,
                             "num_pay": None,
                             "department": department})

    return payments