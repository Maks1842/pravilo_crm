import json
import re

from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_

from src.references.models import ref_tribunal


'''
Изхвлечение мировых судов с сайта ГАС Правосудие (файл index.php)
'''
async def parse_sudrf_index(session):

    path_file = '/home/maks/Загрузки/index.php'

    with open(path_file) as file:
        text = str(file.read())

    class_code_list = re.findall(r"(?<=\[balloons_user\[').+(?='\]\.)", text)
    tribunal_list = re.findall(r"(?<=name:').+(?=',adress)", text)
    address_tribun_list = re.findall(r"(?<=adress:').+(?=',coord)", text)

    count = 0

    for item in class_code_list:
        class_code: str = item

        try:
            data = {
                'class_code': class_code,
                'name': tribunal_list[count],
                'address': address_tribun_list[count]}
            count += 1

            tribunal_qwery = await session.execute(select(ref_tribunal.c.id).where(ref_tribunal.c.class_code == class_code))
            tribunal_id: int = tribunal_qwery.scalar()

            if tribunal_id:
                post_data = update(ref_tribunal).where(ref_tribunal.c.id == tribunal_id).values(data)
            else:
                post_data = insert(ref_tribunal).values(data)

            await session.execute(post_data)
            await session.commit()
        except Exception as ex:
            print(f'{item} {ex}')
            return
    print(count)


    return


'''
Проверка в БД Суда с отметкой "gaspravosudie". При отсутствии - добавляю/изменяю запись о Суде.
Предварительно получаю файл data.json с сайта https://ej.sudrf.ru/, с помощью модуля sudrf_selenium
'''
async def parse_ej_sudrf(session):

    path_file = '/home/maks/Загрузки/data.json'

    with open(path_file) as json_file:
        data = json.load(json_file)

    for item in data['tribunal']:
        class_code: str = item['class_code']

        try:
            data = {
                'class_code': class_code,
                'name': item['name'],
                'address': item['address'],
                'gaspravosudie': True}

            tribunal_qwery = await session.execute(select(ref_tribunal.c.id).where(ref_tribunal.c.class_code == class_code))
            tribunal_id: int = tribunal_qwery.scalar()

            if tribunal_id:
                data_gas = {'gaspravosudie': True}
                post_data = update(ref_tribunal).where(ref_tribunal.c.id == tribunal_id).values(data_gas)
            else:
                post_data = insert(ref_tribunal).values(data)

            await session.execute(post_data)
            await session.commit()
        except Exception as ex:
            print(f'{item} {ex}')
            return

    return



# parse_ej_sudrf()