import pandas as pd
import json
from datetime import datetime, date
import re
import os
from src.config import path_main

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.routers_helper.rout_debt_import.re_pattern_for_excel import RePattern
from src.config import main_dossier_path, logging_path
from src.debts.models import cession, debtor, credit
from src.directory_docs.models import dir_cession, dir_folder, dir_credit
from src.references.models import ref_type_ed, ref_claimer_ed, ref_tribunal, ref_rosp
from src.collection_debt.models import executive_document, executive_productions

import logging
log_path = os.path.join(logging_path, 'upload_to_db.log')
logging.basicConfig(level=logging.DEBUG, filename=log_path, filemode="w", format='%(levelname)s; %(asctime)s; %(filename)s; %(message)s')

'''
НЕОБХОДИМО НАСТРАИВАТЬ ПОД КАЖДЫЙ НОВЫЙ РЕЕСТР


Импорт данных из файлов Excel.
Извлеченные данные попадают на фронтенд, где происходит сопоставление наименований извлеченных заголовков столбцов
с имеющимися полями в DataBase.
С фронта 'excel_field' приходят в виде индексов, которые на бэке изменяются на фактические названия полей Excel.
После сопоставления данные загружаются в DB.

import_excel и format_data - это вспомогательные методы, для форматирования данных (дата, числа, суммы и т.д.)
format_file.xlsx - это дефолтный файл, который создается при выборе csv файла (из выбранного файла, данные перезаписываются в дефолтный).
И уже дефолтный обрабатывается, и из него данные грузятся в БД.

При импортировании реестра должников из Excel в DB_CRM, необходимо чтобы Справочники (Суды, РОСПы, Банки, Статусы, Взыскатель по ИД (Цессионарий) и тд.) были заполнены.
Далее, при импортировании реестров должников (первичная миграция или цессии), производится сопоставление со справочниками,
если сопоставление отсутствует, то в Лог делается запись, что такие-то данные из реестра не загружены из-за отсутствия в Справочнике БД.

'''


# Загрузить реестр должников в БД
router_post_database = APIRouter(
    prefix="/v1/PostDatabase",
    tags=["Import_to_database"]
)


@router_post_database.post("/")
async def add_database(data_dict: dict, session: AsyncSession = Depends(get_async_session)):

    headers_excel = data_dict['headers_excel']
    comparison_excel_to_db = data_dict['comparison_excel_to_db']

    registry_excel = format_data()

    # Сопоставление полей Модели с excel_field, и изменение индексов на фактическое наименование
    for exl in comparison_excel_to_db:
        # for f in exl['fields']:
        for h in headers_excel:
            if exl['excel_field'] == h['value']:
                exl['excel_field'] = h['text']

    count_all = 0
    cessions_count = 0
    debtors_count = 0
    credits_count = 0
    ed_count = 0
    ep_count = 0

    # Сопоставление полей "Поле БД": debt_exl["заголовок из excel"]
    for debt_exl in registry_excel:
        count_all += 1

        cessions_data = {}
        debtors_data = {}
        credits_data = {}
        ed_data = {}
        ep_data = {}

        last_name_1 = None
        first_name_1 = None
        second_name_1 = None
        last_name_2 = None
        first_name_2 = None
        second_name_2 = None
        passport_series = None
        passport_num = None
        passport_date = None
        passport_department = None
        index_1 = None
        address_1 = None
        index_2 = None
        address_2 = None
        comment = None
        inn = None
        phone = None
        type_ed_id = None
        ed_id = None
        claimer_ed_id = None
        tribunal_id = None
        rosp_id = None
        summary_case = None

        for item in comparison_excel_to_db:
            id_dapartment = None
            id_ed = None

            if item['model'] == 'cession':
                try:
                    if item["excel_field"] != '' and item["excel_field"] is not None:
                        if item["name_field"] == 'summa':
                            summa = debt_exl[f'{item["excel_field"]}']
                            cessions_data[f'{item["name_field"]}'] = summa * 100
                        else:
                            cessions_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
                    else:
                        if item["name_field"] != 'None':
                            cessions_data[f'{item["name_field"]}'] = None
                except Exception as ex:
                    return {
                        "status": "error",
                        "data": None,
                        "details": f'Ошибка при извлечении данных из excel в модель cession, на строке {count_all}. {ex}'
                    }

            elif item['model'] == 'debtor':
                try:
                    if item["excel_field"] != '' and item["excel_field"] is not None:
                        if item["headers_key"] == 'fio_debtor':
                            fio = parsing_fio(debt_exl[f'{item["excel_field"]}'])
                            last_name_1 = fio['last_name_1']
                            first_name_1 = fio['first_name_1']
                            second_name_1 = fio['second_name_1']
                            last_name_2 = fio['last_name_2']
                            first_name_2 = fio['first_name_2']
                            second_name_2 = fio['second_name_2']

                            debtors_data['last_name_1'] = last_name_1
                            debtors_data['first_name_1'] = first_name_1
                            debtors_data['second_name_1'] = second_name_1
                            debtors_data['last_name_2'] = last_name_2
                            debtors_data['first_name_2'] = first_name_2
                            debtors_data['second_name_2'] = second_name_2

                        elif item["headers_key"] == 'passport':
                            passport = parsing_passport(debt_exl[f'{item["excel_field"]}'])
                            passport_series = passport['passport_series']
                            passport_num = passport['passport_num']
                            passport_date = passport['passport_date']
                            passport_department = passport['passport_department']

                        elif item["headers_key"] == 'address_registry':
                            addr = parsing_address(debt_exl[f'{item["excel_field"]}'])
                            index_1 = addr['index']
                            address_1 = addr['address']

                        elif item["headers_key"] == 'address_resident':
                            addr_2 = parsing_address(debt_exl[f'{item["excel_field"]}'])
                            index_2 = addr_2['index']
                            address_2 = addr_2['address']

                        elif item["name_field"] == 'comment':
                            comment = short_str_200(debt_exl[f'{item["excel_field"]}'])
                            debtors_data['comment'] = comment

                        elif item["name_field"] == 'inn':
                            inn = format_inn(debt_exl[f'{item["excel_field"]}'])
                            debtors_data['inn'] = inn

                        elif item["name_field"] == 'phone':
                            phone = str(debt_exl[f'{item["excel_field"]}'])
                            debtors_data['phone'] = phone

                        elif item["name_field"] == 'None':
                            pass

                        else:
                            debtors_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
                    else:
                        if item["name_field"] != 'None':
                            debtors_data[f'{item["name_field"]}'] = None


                    debtors_data['passport_series'] = passport_series
                    debtors_data['passport_num'] = passport_num
                    if passport_date:
                        debtors_data['passport_date'] = passport_date
                    if passport_department:
                        debtors_data['passport_department'] = passport_department
                    debtors_data['index_add_1'] = index_1
                    debtors_data['address_1'] = address_1
                    debtors_data['index_add_2'] = index_2
                    debtors_data['address_2'] = address_2

                except Exception as ex:
                    return {
                        "status": "error",
                        "data": None,
                        "details": f'Ошибка при извлечении данных из excel в модель debtor, на строке {count_all}. {ex}'
                    }

            elif item['model'] == 'credit':
                try:
                    if item["excel_field"] != '' and item["excel_field"] is not None:
                        if item["name_field"] == 'summa' or item["name_field"] == 'summa_by_cession' or \
                                item["name_field"] == 'overdue_od' or item["name_field"] == 'overdue_percent' or item["name_field"] == 'penalty' or \
                                item["name_field"] == 'percent_of_od' or item["name_field"] == 'gov_toll' or item["name_field"] == 'balance_debt':
                            summa = debt_exl[f'{item["excel_field"]}']
                            credits_data[f'{item["name_field"]}'] = int(summa * 100)
                        elif item["name_field"] == 'interest_rate':
                            try:
                                summa = debt_exl[f'{item["excel_field"]}']
                                credits_data[f'{item["name_field"]}'] = summa
                            except:
                                credits_data[f'{item["name_field"]}'] = None
                        elif item["name_field"] == 'number' or item["name_field"] == 'date_end':
                            credits_data[f'{item["name_field"]}'] = str(debt_exl[f'{item["excel_field"]}'])

                        else:
                            credits_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
                    else:
                        if item["name_field"] != 'None':
                            credits_data[f'{item["name_field"]}'] = None


                    try:
                        credits_data['creditor'] = cessions_data['cedent']
                    except:
                        credits_data['creditor'] = 'Кредитор'
                    credits_data['status_cd_id'] = 2


                except Exception as ex:
                    return {
                        "status": "error",
                        "data": None,
                        "details": f'Ошибка при извлечении данных из excel в модель credit, на строке {count_all}. {ex}'
                    }

            elif item['model'] == 'executive_document':
                try:
                    if item["excel_field"] != '' and item["excel_field"] is not None:
                        if item["name_field"] == 'type_ed_id':
                            type_ed = parsing_type_ed(debt_exl[f'{item["excel_field"]}'])

                            type_ed_query = await session.execute(select(ref_type_ed.c.id).where(ref_type_ed.c.name == str(type_ed)))
                            type_ed_id = type_ed_query.scalar()
                        elif item["name_field"] == 'claimer_ed_id':
                            claimer_ed = debt_exl[f'{item["excel_field"]}']
                            claimer_ed_query = await session.execute(select(ref_claimer_ed.c.id).where(ref_claimer_ed.c.name == str(claimer_ed)))
                            claimer_ed_id = claimer_ed_query.scalar()
                            if claimer_ed_id is None:
                                logging.debug(f"По КД {credits_data['number']}, Взыскатель ({claimer_ed}) не найден")

                        elif item["headers_key"] == 'tribunal_name_ed':
                            tribunal = parsing_type_ed(debt_exl[f'{item["excel_field"]}'])
                            tribunal_query = await session.execute(select(ref_tribunal.c.id).where(and_(ref_tribunal.c.name == str(tribunal))))
                            tribunal_id = tribunal_query.scalar()
                            if tribunal_id is None:
                                logging.debug(f"По КД {credits_data['number']}, Суд ({tribunal}) не найден")

                        else:
                            ed_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
                    else:
                        if item["name_field"] != 'None':
                            ed_data[f'{item["name_field"]}'] = None

                    ed_data['type_ed_id'] = type_ed_id
                    ed_data['status_ed_id'] = 1
                    ed_data['claimer_ed_id'] = claimer_ed_id
                    ed_data['tribunal_id'] = tribunal_id
                except Exception as ex:
                    return {
                        "status": "error",
                        "data": None,
                        "details": f'Ошибка при извлечении данных из excel в модель executive_document, на строке {count_all}. {ex}'
                    }

            elif item['model'] == 'executive_productions':
                try:
                    if item["excel_field"] != '' and item["excel_field"] is not None:
                        if item["name_field"] == 'rosp_id':
                            rosp = debt_exl[f'{item["excel_field"]}']
                            rosp_query = await session.execute(select(ref_rosp.c.id).where(ref_rosp.c.name == str(rosp)))
                            rosp_id = rosp_query.scalar()
                            if rosp_id is None:
                                logging.debug(f"По КД {credits_data['number']}, РОСП ({rosp}) не найден")
                        elif item["name_field"] == 'summary_case':
                            summary_case = debt_exl[f'{item["excel_field"]}']
                            if summary_case == 0 or summary_case == '':
                                summary_case = None
                        else:
                            ep_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
                    else:
                        if item["name_field"] != 'None':
                            ep_data[f'{item["name_field"]}'] = None

                    ep_data['rosp_id'] = rosp_id
                    ep_data['summary_case'] = summary_case
                except Exception as ex:
                    return {
                        "status": "error",
                        "data": None,
                        "details": f'Ошибка при извлечении данных из excel в модель executive_productions, на строке {count_all}. {ex}'
                    }

            elif item['model'] == 'ref_tribunal':
                try:
                    if item["excel_field"] != '' and item["excel_field"] is not None:
                        if item["name_field"] == 'class_code':
                            class_code: str = debt_exl[f'{item["excel_field"]}']
                            tribunal_id_query = await session.execute(select(ref_tribunal.c.id).where(ref_tribunal.c.class_code == class_code))
                            tribunal_id = tribunal_id_query.scalar()

                    debtors_data['tribunal_id'] = tribunal_id
                except Exception as ex:
                    return {
                        "status": "error",
                        "data": None,
                        "details": f'Ошибка при извлечении данных из excel в модель executive_document, на строке {count_all}. {ex}'
                    }

        """
        При импортировании реестра должников из Excel в DB_CRM, необходимо чтобы Справочники (Суды, РОСПы, Банки, Статусы, Взыскатель по ИД (Цессионарий) и тд.) были заполнены.
        Далее, при импортировании реестров должников (первичная миграция или цессии), производится сопоставление со справочниками,
        если сопоставление отсутствует, то в Лог делается запись, что такие-то данные из реестра не загружены из-за отсутствия в Справочнике БД.
        """

        # Блок сохранения данных в модель cession
        cession_query = await session.execute(select(cession.c.id, cession.c.name).where(and_(cession.c.name == cessions_data['name'],
                                                                              cession.c.number == str(cessions_data['number']))))
        cession_item = cession_query.mappings().fetchone()
        if cession_item is not None:
            cession_id = cession_item['id']
            name_cession = cession_item['name']

            path = create_dir_cession(name_cession)
            path_folder_cd = path['path_folder']
        else:
            post_data = insert(cession).values(cessions_data)

            try:
                await session.execute(post_data)
                await session.commit()

                cession_query = await session.execute(select(cession).order_by(desc(cession.c.id)))
                cession_dict = cession_query.mappings().first()

                # cession_dict = dict(item._mapping)

                cession_id = cession_dict['id']
                name_cession = cession_dict['name']

                path = create_dir_cession(name_cession)
                path_cession = path['path_cession']
                path_folder_cd = path['path_folder']


                dir_cession_data = {
                    "cession_id": cession_id,
                    "name": name_cession,
                    "path": path_cession,
                }
                query = await session.execute(select(dir_cession.c.cession_id).where(dir_cession.c.cession_id == int(cession_id)))
                dir_cession_id = query.scalar()

                if dir_cession_id is None:

                    post_data = insert(dir_cession).values(dir_cession_data)

                    try:
                        await session.execute(post_data)
                        await session.commit()
                    except Exception as ex:
                        return {
                            "status": "error",
                            "data": dir_cession_data,
                            "details": f'Ошибка при сохранении в модель dir_cession. {ex}'
                        }

                cessions_count += 1
            except Exception as ex:
                return {
                    "status": "error",
                    "data": cessions_data,
                    "details": f'Ошибка при сохранении в модель cession, на строке {count_all}. {ex}'
                }

        # Блок сохранения данных в модель debtor
        if debtors_data['second_name_1'] is not None and debtors_data['second_name_1'] != '':
            debtor_query = await session.execute(select(debtor.c.id).where(and_(debtor.c.last_name_1 == debtors_data['last_name_1'],
                                                                  debtor.c.first_name_1 == debtors_data['first_name_1'],
                                                                  debtor.c.second_name_1 == debtors_data['second_name_1'],
                                                                  debtor.c.birthday == debtors_data['birthday'])))
        else:
            debtor_query = await session.execute(select(debtor.c.id).where(and_(debtor.c.last_name_1 == debtors_data['last_name_1'],
                                                                                debtor.c.first_name_1 == debtors_data['first_name_1'],
                                                                                debtor.c.birthday == debtors_data['birthday'])))

        debtor_id = debtor_query.scalar()

        if debtor_id is None:
            post_data = insert(debtor).values(debtors_data)

            try:
                await session.execute(post_data)
                await session.commit()

                debtor_query = await session.execute(select(debtor.c.id).order_by(desc(debtor.c.id)))
                debtor_id = debtor_query.scalar()

                debtors_count += 1
            except Exception as ex:
                return {
                    "status": "error",
                    "data": debtors_data,
                    "details": f'Ошибка при сохранении в модель Debtors, на строке {count_all}. {ex}'
                }

        # Блок сохранения данных в модель credit
        credit_query = await session.execute(select(credit.c.id, credit.c.number).where(and_(credit.c.creditor == credits_data['creditor'],
                                                                            credit.c.number == str(credits_data['number']))))
        credits_data['debtor_id'] = debtor_id
        credits_data['cession_id'] = cession_id
        credit_item = credit_query.mappings().fetchone()
        if credit_item is not None:
            credit_id = credit_item['id']
            credit_number = credit_item['number']

            dossier_name = f"{debtors_data['last_name_1']} {debtors_data['first_name_1']}_{credit_number}"
            query_folder = await session.execute(select(dir_folder))
            folders = query_folder.mappings().all()

            path = create_dir_credit(dossier_name, path_folder_cd, folders)
            # path_credit = path['path_credit']
        else:
            post_data = insert(credit).values(credits_data)

            try:
                await session.execute(post_data)
                await session.commit()

                credit_query = await session.execute(select(credit).order_by(desc(credit.c.id)))
                credit_dict = credit_query.mappings().first()

                credit_id = credit_dict['id']
                credit_number = credit_dict['number']

                dossier_name = f"{debtors_data['last_name_1']} {debtors_data['first_name_1']}_{credit_number}"
                query_folder = await session.execute(select(dir_folder))
                folders = query_folder.mappings().all()

                path = create_dir_credit(dossier_name, path_folder_cd, folders)
                path_credit = path['path_credit']


                dir_credit_data = {
                    "credit_id": credit_id,
                    "name": dossier_name,
                    "path": path_credit,
                }
                query = await session.execute(select(dir_credit.c.credit_id).where(dir_credit.c.credit_id == int(credit_id)))
                dir_credit_id = query.scalar()

                if dir_credit_id is None:

                    post_data = insert(dir_credit).values(dir_credit_data)

                    try:
                        await session.execute(post_data)
                        await session.commit()
                    except Exception as ex:
                        return {
                            "status": "error",
                            "data": dir_credit_data,
                            "details": f'Ошибка при сохранении в модель dir_credit. {ex}'
                        }

                credits_count += 1
            except Exception as ex:
                return {
                    "status": "error",
                    "data": credits_data,
                    "details": f'Ошибка при сохранении в модель credit, на строке {count_all}. {ex}'
                }

        # Блок сохранения данных в модель executive_document
        if ed_data['number'] is not None:
            ed_query = await session.execute(select(executive_document.c.id).where(and_(executive_document.c.number == str(ed_data['number']),
                                                                                                         executive_document.c.date == ed_data['date'],
                                                                                                         executive_document.c.case_number == str(ed_data['case_number']))))
            ed_data['credit_id'] = credit_id
            ed_id = ed_query.scalar()

            if ed_id is None:
                post_data = insert(executive_document).values(ed_data)

                try:
                    await session.execute(post_data)
                    await session.commit()

                    ed_query = await session.execute(select(executive_document.c.id).order_by(desc(executive_document.c.id)))
                    ed_id = ed_query.scalar()

                    ed_count += 1
                except Exception as ex:
                    return {
                        "status": "error",
                        "data": ed_data,
                        "details": f'Ошибка при сохранении в модель executive_document, на строке {count_all}. {ex}'
                    }

        # Блок сохранения данных в модель executive_productions
        if ep_data['number'] is not None:
            ep_query = await session.execute(select(executive_productions.c.id).where(executive_productions.c.number == str(ep_data['number'])))
            ep_data['credit_id'] = credit_id
            ep_data['executive_document_id'] = ed_id
            ep_id = ep_query.scalar()

            if ep_id is None:
                post_data = insert(executive_productions).values(ep_data)

                try:
                    await session.execute(post_data)
                    await session.commit()

                    ep_count += 1
                except Exception as ex:
                    return {
                        "status": "error",
                        "data": ep_data,
                        "details": f'Ошибка при сохранении в модель executive_productions, на строке {count_all}. {ex}'
                    }

    result = f'Добавлено: {cessions_count} строк Цессий, ' \
             f'{debtors_count} строк ФИО должников, ' \
             f'{credits_count} строк Кредитов, ' \
             f'{ed_count} строк ИД, ' \
             f'{ep_count} строк ИП'

    return {
        'status': 'success',
        'data': result,
        'details': 'Данные успешно сохранены.'
    }

'''
import_excel и format_data - это вспомогательные методы, для форматирования данных (дата, числа, суммы и т.д.)
format_file.xlsx - это дефолтный файл, который создается при выборе excel файла (из выбранного файла, данные перезаписываются в дефолтный).
И уже дефолтный обрабатывается, и из него данные грузятся в БД.
'''
def import_excel():
    excel_data = pd.read_excel(f'{path_main}/src/media/data/format_file.xlsx')
    json_str = excel_data.to_json(orient='records', date_format='iso')
    parsed = json.loads(json_str)
    return parsed


def format_data():
    data_excel = import_excel()

    result = []
    for data in data_excel:
        dict = {}
        for key in data:
            item = data[key]

            # Удаляю лишние пробелы, переносы строк
            try:
                x = re.sub(r'^[\s-]+|\s+$|\n+|^\s+', '', item)
            except:
                x = item

            # Дату формата дд.мм.гггг привожу к формату для БД
            try:
                if re.findall(r'\d{2}\.\d{2}\.\d{4}', x):
                    x = datetime.strptime(x, '%d.%m.%Y').date()
            except:
                pass

            try:
                x = datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f').date()
            except:
                pass

            # В числе, запятую заменить на точку
            try:
                summa = re.search(r'\d+,\d{1,2}', x).group()
                x = re.sub(r',', '.', summa)
            except:
                pass

            dict.update({key: x})
        result.append(dict)

    return result


def format_inn(inn):
    # ИНН - формат числа привожу к строке и извлекаю 12 цифр
    try:
        inn = re.search(r'\d{10,12}', str(inn)).group()
    except Exception:
        inn = None
    return inn


def parsing_fio(fio):

    if "(" in fio:
        fio_1_sp = re.search(RePattern.fio_1, fio).group().strip()
        fio_2_sp = re.search(RePattern.fio_2, fio).group().strip()

        last_name_1 = fio
        first_name_1 = 'ОШИБКА'
        second_name_1 = None
        last_name_2 = None
        first_name_2 = None
        second_name_2 = None
        if len(re.split("\s+", fio_1_sp)) > 1 and len(re.split("\s+", fio_2_sp)) > 1:
            fio_split_1 = split_fio(fio_1_sp)
            fio_split_2 = split_fio(fio_2_sp)

            last_name_1 = fio_split_1['last_name']
            first_name_1 = fio_split_1['first_name']
            second_name_1 = fio_split_1['second_name']
            last_name_2 = fio_split_2['last_name']
            first_name_2 = fio_split_2['first_name']
            second_name_2 = fio_split_2['second_name']

        elif ' ' not in fio_1_sp and ' ' not in fio_2_sp:
            var_1 = re.sub('\(\D+\)', '', fio)
            var_2 = re.sub('[\D]+\)', fio_2_sp, fio)
            fio_split_1 = split_fio(var_1)
            fio_split_2 = split_fio(var_2)

            last_name_1 = fio_split_1['last_name']
            first_name_1 = fio_split_1['first_name']
            second_name_1 = fio_split_1['second_name']
            last_name_2 = fio_split_2['last_name']
            first_name_2 = fio_split_2['first_name']
            second_name_2 = fio_split_2['second_name']
    else:
        fio_split = split_fio(fio)

        last_name_1 = fio_split['last_name']
        first_name_1 = fio_split['first_name']
        second_name_1 = fio_split['second_name']
        last_name_2 = None
        first_name_2 = None
        second_name_2 = None

    result = {'last_name_1': last_name_1,
              'first_name_1': first_name_1,
              'second_name_1': second_name_1,
              'last_name_2': last_name_2,
              'first_name_2': first_name_2,
              'second_name_2': second_name_2}

    return result


def split_fio(fio):
    fio_strip = fio.strip()

    fio_str = re.split("\s+", fio_strip)

    if len(fio_str) == 2:
        last_name = fio_str[0]
        first_name = fio_str[1]
        second_name = ''
    elif len(fio_str) == 3:
        last_name = fio_str[0]
        first_name = fio_str[1]
        second_name = fio_str[2]
    else:
        last_name = fio_str[0]
        first_name = fio_str[1]
        second_name = f'{" ".join(fio_str[2:])}'

    result = {'last_name': last_name, 'first_name': first_name, 'second_name': second_name}

    return result


def parsing_passport(passport):
    try:
        passport_series_sp = re.search(RePattern.passport_series, passport).group().strip()
        passport_series = re.sub(r'\s*', '', passport_series_sp)
    except:
        passport_series = None

    try:
        passport_num = re.search(RePattern.passport_num, passport).group().strip()
    except:
        passport_num = None

    try:
        passport_dep = re.search(RePattern.passport_department, passport).group().strip()
        passport_department = re.sub(r' \d{2}\.\d{2}\.\d{4}| \d{2}\.\d{2}\.\d{2}', '', passport_dep)
    except:
        passport_department = None

    try:
        passport_date_re = re.search(RePattern.passport_date, passport).group().strip()
        passport_date = datetime.strptime(passport_date_re, '%d.%m.%Y').date()
    except:
        passport_date = None

    result = {'passport_series': passport_series,
              'passport_num': passport_num,
              'passport_date': passport_date,
              'passport_department': passport_department}

    return result


def parsing_address(addr):
    try:
        index = re.search(RePattern.index_re, addr).group().strip()
    except:
        index = None

    try:
        address = re.search(RePattern.address_re, addr).group().strip()
        if len(address) > 200:
            address = address[-200:]
    except:
        address = None

    result = {'index': index,
              'address': address}

    return result


def parsing_type_ed(type):
    try:
        if re.findall(r'(?i)исполнительный\s+лист', type):
            type = 'Исполнительный лист (бланк)'
        elif re.findall(r'(?i)судебный\s+приказ', type):
            type = 'Судебный приказ'
    except:
        type = 'Не определен'

    return type


def parsing_date_ed(date):
    try:
        date_ed_re = re.search(r'\d{4}-\d{2}-\d{2}', date).group()
        date_ed = datetime.strptime(date_ed_re, '%d.%m.%Y').date()
    except:
        date_ed = None

    return date_ed


def parsing_date_start(date_st):
    try:
        date_start = re.search(r'\d{4}-\d{2}-\d{2}', date_st).group()
    except:
        date_start = date.today()

    return date_start


# Извлечь ПЕРВЫЕ 50 символов из строки
def short_str_50(data_str):
    try:
        if len(data_str) > 50:
            data_str = data_str[:50]
    except:
        pass
    return data_str


# Извлечь ПОСЛЕДНИЕ 200 символов из строки
def short_str_200(data_str):
    try:
        if len(data_str) > 200:
            data_str = data_str[-200:]
    except:
        pass
    return data_str


def short_str_100(data_str):
    try:
        if len(data_str) > 100:
            data_str = data_str[-100:]
    except:
        pass
    return data_str


def parsing_execut_production(ep):
    try:
        execut_production = re.search(RePattern.execut_production, ep).group().strip()
    except:
        execut_production = None

    try:
        date = re.search(RePattern.date_ep, ep).group().strip()
        date_ep = datetime.strptime(date, '%d.%m.%Y').strftime("%Y-%m-%d")
    except:
        date_ep = None

    try:
        consolidat_ep = re.search(RePattern.consolidat_ep, ep).group().strip()
    except:
        consolidat_ep = None

    result = {'execut_production': execut_production,
              'date_ep': date_ep,
              'consolidat_ep': consolidat_ep}

    return result


def create_dir_cession(name_cession):

    path = os.path.join(main_dossier_path, name_cession)
    folders = ['Договор цессии', 'Кредитные досье']

    if not os.path.exists(path):
        os.mkdir(path)

    path_folder = ''
    for f in folders:
        path_folder = os.path.join(path, f)
        if not os.path.exists(path_folder):
            os.mkdir(path_folder)

    return {'path_cession': path, 'path_folder': path_folder}

def create_dir_credit(dossier_name, path_folder_cd, folders):

    path = os.path.join(path_folder_cd, dossier_name)

    if not os.path.exists(path):
        os.mkdir(path)

    for f in folders:
        path_folder = os.path.join(path, f['name'])
        if not os.path.exists(path_folder):
            os.mkdir(path_folder)

    return {'path_credit': path}


