import re
import pandas as pd
import json
from src.routers_helper.rout_debt_import.re_pattern_for_excel import RePattern

from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from src.references.models import ref_rosp


'''
Изхвлечение РОСП из файла Excel
'''

def import_excel():
    excel_data = pd.read_excel(f'/home/maks/Загрузки/Реестр отделов РОСП_для CRM.xlsx')
    json_str = excel_data.to_json(orient='records', date_format='iso')
    parsed = json.loads(json_str)
    return parsed


async def extract_rosp_excel(session):
    data_excel = import_excel()

    index = None
    address = None

    count = 0
    for item in data_excel:

        class_code = str(item['class_code'])
        if len(class_code) == 4:
            class_code = f'0{class_code}'

        if item['address']:
            try:
                index = re.search(RePattern.index_re, item['address']).group().strip()
            except:
                index = None

            try:
                address = re.search(RePattern.address_re, item['address']).group().strip()
                if len(address) > 200:
                    address = address[-200:]
            except:
                address = None
        data = {
            'type_department_id': item['type_department_id'],
            'name': item['name'],
            'address_index': index,
            'address': address,
            'phone': str(item['telephone']),
            'class_code': str(class_code),
        }

        try:
            count += 1

            rosp_qwery = await session.execute(select(ref_rosp.c.id).where(ref_rosp.c.class_code == str(class_code)))
            rosp_id: int = rosp_qwery.scalar()

            if rosp_id:
                post_data = update(ref_rosp).where(ref_rosp.c.id == rosp_id).values(data)
            else:
                post_data = insert(ref_rosp).values(data)

            await session.execute(post_data)
            await session.commit()
        except Exception as ex:
            print(f'Ошибка на строке {count} {item} {ex}')
            return f'Ошибка на строке {count} {item} {ex}'

    print(count)

    return f'Загружено {count} РОСП'



# format_data()