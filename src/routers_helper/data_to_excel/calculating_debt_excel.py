from openpyxl import load_workbook
from datetime import datetime

from src.routers_helper.data_to_excel.style_excel import style_excel
from src.config import path_main

async def calculating_debt_to_excel(data_json, session):

    style = style_excel()

    book_template = load_workbook(filename=f'{path_main}/src/media/calculating_debt/template_calculating_debt.xlsx')

    # Первый (активный) Лист книги
    sheet = book_template.active

    # Изменить имя Листа книги
    sheet.title = "Расчет"

    count = 0
    number_col = 1
    number_row = 2
    for data in data_json['data_json']:
        count += 1

        number_col += 1

        # # Вставить один столбец перед №___
        # sheet.insert_cols(number_col)

        column = 1
        row = number_row

        # Высота строки
        sheet.row_dimensions[row].height = 50

        # Ширина столбца
        sheet.column_dimensions["A"].width = 60
        sheet.column_dimensions["B"].width = 60
        sheet.column_dimensions["C"].width = 15
        sheet.column_dimensions["D"].width = 30
        sheet.column_dimensions["E"].width = 70
        sheet.column_dimensions["F"].width = 20
        sheet.column_dimensions["G"].width = 20
        sheet.column_dimensions["H"].width = 30
        sheet.column_dimensions["I"].width = 30
        sheet.column_dimensions["J"].width = 30
        sheet.column_dimensions["K"].width = 30

        try:
            # Добавить данные в ячейку
            column = 1
            sheet.cell(row, column).value = data['addressRecipient']
            sheet.cell(row, column).style = style['style_main']
            # print('1')

            column = 2
            sheet.cell(row, column).value = data['mailRecipient']
            sheet.cell(row, column).style = style['style_main']
            # print('2')

            column = 3
            sheet.cell(row, column).value = data['mailMass']
            sheet.cell(row, column).style = style['style_main']
            # print('3')

            column = 4
            sheet.cell(row, column).value = f"№ {data['sequenceNum']} от {data['mailDate']}, {data['docName']}"
            sheet.cell(row, column).style = style['style_main']
            # print('4')

            column = 5
            sheet.cell(row, column).value = f"{data['debtorName']}, {data['caseNum']}"
            sheet.cell(row, column).style = style['style_main']
            # print('5')

            column = 6
            sheet.cell(row, column).value = data['mailType']['value']
            sheet.cell(row, column).style = style['style_main']
            # print('6')

            column = 7
            sheet.cell(row, column).value = '355011'
            sheet.cell(row, column).style = style['style_main']
            # print('7')

            column = 8
            sheet.cell(row, column).value = data['packageType']
            sheet.cell(row, column).style = style['style_main']
            # print('8')

            column = 9
            sheet.cell(row, column).value = 'S'
            sheet.cell(row, column).style = style['style_main']
            # print('9')

            column = 10
            sheet.cell(row, column).value = ''
            sheet.cell(row, column).style = style['style_main']
            # print('10')

            column = 11
            sheet.cell(row, column).value = ''
            sheet.cell(row, column).style = style['style_main']
            # print('11')
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": f'Почтовый реестр не сформирован. Предоставлены не все данные. Ошибка на строке {row} {ex}'
            }

        number_row += 1

    current_date = datetime.now()
    file = f'{path_main}/src/media/mail/result/Исходящая почта_{current_date.strftime("%d.%m.%Y_%H.%M.%S")}.xlsx'
    book_template.save(file)

    return {
        'status': 'success',
        'data': None,
        'details': 'Почтовый реестр Excel успешно сформирован'
    }