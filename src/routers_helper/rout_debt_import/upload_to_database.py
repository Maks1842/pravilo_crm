import pandas as pd
import json
from datetime import datetime, date
import re
from src.routers_helper.rout_debt_import.re_pattern_for_excel import RePattern

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import cession, debtor, credit

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

При первичной миграции реестра должников из Excel в DB_CRM, в первую очередь необходимо импортировать Справочники (Суды, РОСПы, статусы и тд.)
Далее, при импортировании реестров должников (первичная миграция или цессии), производится сопоставление со справочниками,
если сопоставление отсутствует, то в Лог делается запись, что такие-то данные из реестра не загружены из-за отсутствия в Справочнике БД.

'''
import logging
debug_log = logging.getLogger('debug_log')
# error_log = logging.getLogger('error_log')
upload_log = logging.getLogger('upload_log')


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
    tribunals_count = 0
    dapartment_present_count = 0
    ed_count = 0
    ep_count = 0
    collection_debt_count = 0

    # Сопоставление полей "Поле БД": debt_exl["заголовок из excel"]
    for debt_exl in registry_excel:
        count_all += 1

        cessions_data = {}
        debtors_data = {}
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

                        elif item["headers_key"] == 'address_1':
                            addr = parsing_address(debt_exl[f'{item["excel_field"]}'])
                            index_1 = addr['index']
                            address_1 = addr['address']

                        elif item["headers_key"] == 'address_2':
                            addr = parsing_address(debt_exl[f'{item["excel_field"]}'])
                            index_2 = addr['index']
                            address_2 = addr['address']

                        elif item["name_field"] == 'comment':
                            comment = short_str_200(debt_exl[f'{item["excel_field"]}'])
                            debtors_data['comment'] = comment

                        elif item["name_field"] == 'inn':
                            inn = format_inn(debt_exl[f'{item["excel_field"]}'])
                            debtors_data['inn'] = inn

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


        cession_query = await session.execute(select(cession.c.id).where(and_(cession.c.name == cessions_data['name'],
                                                                              cession.c.number == cessions_data['number'])))
        cession_id = cession_query.scalar()

        if cession_id is None:
            post_data = insert(cession).values(cessions_data)

            try:
                await session.execute(post_data)
                await session.commit()

                cession_query = await session.execute(select(cession).order_by(desc(cession.c.id)))
                item = cession_query.first()

                cession_dict = dict(item._mapping)
                print(f'{cession_dict=}')

                cession_id = cession_dict['id']
                name_cession = cession_dict['name']

                create_dir = create_dir_cession(name_cession)

                cessions_count += 1
            except Exception as ex:
                return {
                    "status": "error",
                    "data": cessions_data,
                    "details": f'Ошибка при сохранении в модель cession, на строке {count_all}. {ex}'
                }


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

#
#
#                 if comparison['model']['name_mdl'] == 'Credits':
#                     try:
#                         credits_data = {}
#                         status_cd_id = 1
#
#                         for f in comparison['fields']:
#                             if item["excel_field"] != '' and item["excel_field"] is not None:
#                                 if item["name_field"] == 'status_cd':
#                                     status_cd_id = parsing_status_cd(debt_exl[f'{item["excel_field"]}'])
#
#                                 elif item["name_field"] == 'summa' or item["name_field"] == 'summa_by_cession' or item["name_field"] == 'interest_rate' or item["name_field"] == 'overdue_od' or \
#                                         item["name_field"] == 'overdue_percent' or item["name_field"] == 'penalty' or item["name_field"] == 'percent_of_od' \
#                                         or item["name_field"] == 'gov_toll' or item["name_field"] == 'balance_debt':
#                                     try:
#                                         summa = debt_exl[f'{item["excel_field"]}']
#                                         credits_data[f'{item["name_field"]}'] = float(round(summa, 2))
#                                     except:
#                                         credits_data[f'{item["name_field"]}'] = 0
#                                 elif item["name_field"] == 'date_start':
#                                     date_start = parsing_date_start(debt_exl[f'{item["excel_field"]}'])
#                                     credits_data[f'{item["name_field"]}'] = date_start
#                                 else:
#                                     credits_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
#                             else:
#                                 if item["name_field"] == 'summa' or item["name_field"] == 'summa_by_cession' or item["name_field"] == 'interest_rate' or item["name_field"] == 'overdue_od' or \
#                                         item["name_field"] == 'overdue_percent' or item["name_field"] == 'penalty' or item["name_field"] == 'percent_of_od' \
#                                         or item["name_field"] == 'gov_toll' or item["name_field"] == 'balance_debt':
#                                     credits_data[f'{item["name_field"]}'] = 0
#                                 else:
#                                     credits_data[f'{item["name_field"]}'] = ''
#
#                         credits_data['creditor'] = 'Кредитор'
#                         credits_data['status_cd'] = status_cd_id
#                         credits_data['debtor'] = id_debtor
#                         credits_data['cession'] = id_cession
#                     except Exception as ex:
#                         return Response({"error": f'Ошибка при извлечении данных из excel в модель Credits, на строке {count_all}. {ex}'})
#
#                     #             test_data.append(credits_data)
#                     # return Response({'test_data': test_data, 'count': debtors_count})
#
#                     if Credits.objects.filter(creditor=credits_data['creditor'], number=credits_data['number']).exists():
#                         id_credit = Credits.objects.filter(creditor=credits_data['creditor']).get(number=credits_data['number']).id
#                     else:
#                         try:
#                             credits_serializers = CreditsSerializer(data=credits_data)
#                             credits_serializers.is_valid(raise_exception=True)
#                             obj_credits = credits_serializers.save()
#                             id_credit = obj_credits.pk
#
#                             # id_credit = count_all
#                             credits_count += 1
#                         except Exception as ex:
#                             return Response({"error": f'Ошибка при сохранении в модель Credits, на строке {count_all}. {ex}', "credits_data": credits_data})
#
#
#
#                 # При первичной миграции реестра должников из Excel в DB_CRM, в первую очередь необходимо импортировать Справочники (Суды, РОСПы, статусы и тд.)
#                 # Далее, при импортировании реестров должников (первичная миграция или цессии), производится сопоставление со справочниками,
#                 # если сопоставление отсутствует, то в Лог делается запись, что такие-то данные из реестра не загружены из-за отсутствия в Справочнике БД.
#                 elif comparison['model']['name_mdl'] == 'Lib_Tribunals':
#                     try:
#                         email = ''
#                         tribunals_data = {}
#                         for f in comparison['fields']:
#                             if item["excel_field"] != '' and item["excel_field"] is not None:
#                                 if item["name_field"] == 'email':
#                                     email = short_str_100(debt_exl[f'{item["excel_field"]}'])
#                                 else:
#                                     tribunals_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
#                             else:
#                                 tribunals_data[f'{item["name_field"]}'] = ''
#                         tribunals_data['email'] = email
#                     except Exception as ex:
#                         return Response({"error": f'Ошибка при извлечении данных из excel в модель Lib_Tribunals, на строке {count_all}. {ex}'})
#
#                     #             test_data.append(tribunals_data)
#                     # return Response({'test_data': test_data, 'count': debtors_count})
#
#                     if Lib_Tribunals.objects.filter(name=tribunals_data['name']).exists():
#                         id_tribunal = Lib_Tribunals.objects.get(name=tribunals_data['name']).id
#                     else:
#                         id_tribunal = None
#                         upload_log.debug(f"По КД {credits_data['number']}, Суд ({tribunals_data['name']}) не найден")
#                         # try:
#                         #     if tribunals_data['name'] is not None and tribunals_data['name'] != '':
#                         #         tribunals_serializers = Lib_TribunalsSerializer(data=tribunals_data)
#                         #         tribunals_serializers.is_valid(raise_exception=True)
#                         #         obj_tribunal = tribunals_serializers.save()
#                         #         id_tribunal = obj_tribunal.pk
#                         #
#                         #         # id_tribunal = count_all
#                         #         tribunals_count += 1
#                         # except Exception as ex:
#                         #     return Response({"error": f'Ошибка при сохранении в модель Lib_Tribunals, на строке {count_all}. {ex}', "tribunals_data": tribunals_data})
#
#                 elif comparison['model']['name_mdl'] == 'Executive_Documents':
#                     try:
#                         type_id = None
#                         claimer_id = None
#                         comment = ''
#                         num_ed = None
#                         status_ed_id = None
#
#                         ed_data = {}
#                         for f in comparison['fields']:
#                             if item["excel_field"] != '' and item["excel_field"] is not None:
#                                 if item["name_field"] == 'type_ed':
#                                     type_ed_id = parsing_type_ed(debt_exl[f'{item["excel_field"]}'])
#                                     type_id = type_ed_id
#                                 elif item["name_field"] == 'claimer_ed':
#                                     claimer_ed_id = parsing_claimer_ed(debt_exl[f'{item["excel_field"]}'])
#                                     claimer_id = claimer_ed_id
#                                 elif item["name_field"] == 'number':
#                                     num_ed = short_str_50(debt_exl[f'{item["excel_field"]}'])
#                                 elif item["name_field"] == 'status_ed':
#                                     status_ed_id = parsing_status_ed(debt_exl[f'{item["excel_field"]}'])
#                                 else:
#                                     if item["name_field"] == 'summa_debt_decision' or item["name_field"] == 'state_duty':
#                                         try:
#                                             summa = debt_exl[f'{item["excel_field"]}']
#                                             ed_data[f'{item["name_field"]}'] = float(round(summa, 2))
#                                         except:
#                                             ed_data[f'{item["name_field"]}'] = 0
#                                     elif item["name_field"] == 'date' or item["name_field"] == 'date_of_receipt_ed' or item["name_field"] == 'date_decision' or item["name_field"] == 'succession':
#                                         date_ed = parsing_date_ed(debt_exl[f'{item["excel_field"]}'])
#                                         ed_data[f'{item["name_field"]}'] = date_ed
#                                     elif item["name_field"] == 'comment':
#                                         comment = short_str_200(debt_exl[f'{item["excel_field"]}'])
#                                     else:
#                                         ed_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
#                             else:
#                                 if item["name_field"] == 'summa_debt_decision' or item["name_field"] == 'state_duty':
#                                     ed_data[f'{item["name_field"]}'] = 0
#                                 else:
#                                     ed_data[f'{item["name_field"]}'] = ''
#
#                         ed_data['number'] = num_ed
#                         ed_data['type_ed'] = type_id
#                         ed_data['claimer_ed'] = claimer_id
#                         ed_data['comment'] = comment
#                         ed_data['status_ed'] = status_ed_id
#                         ed_data['credit'] = id_credit
#                         ed_data['tribunal'] = id_tribunal
#                         ed_data['date_entry_force'] = None
#                         ed_data['date_of_receipt_ed'] = None
#                         ed_data['succession'] = None
#                     except Exception as ex:
#                         return Response({"error": f'Ошибка при извлечении данных из excel в модель Executive_Documents, на строке {count_all}. {ex}'})
#
#                     # test_data.append(ed_data)
#                     # return Response({'test_data': test_data, 'count': debtors_count})
#
#                     if Executive_Documents.objects.filter(number=ed_data['number'], date=ed_data['date'], case_number=ed_data['case_number']).exists():
#                         id_ed = Executive_Documents.objects.filter(number=ed_data['number'], date=ed_data['date']).get(case_number=ed_data['case_number']).id
#                     else:
#                         try:
#                             ed_serializers = Executive_DocumentsSerializer(data=ed_data)
#                             ed_serializers.is_valid(raise_exception=True)
#                             ed_obj = ed_serializers.save()
#                             id_ed = ed_obj.pk
#
#                             # id_ed = count_all
#                             ed_count += 1
#                         except Exception as ex:
#                             return Response({"error": f'Ошибка при сохранении в модель Executive_Documents, на строке {count_all}. {ex}', "ed_data": ed_data})
#
#
#                 elif comparison['model']['name_mdl'] == 'Lib_Department_Presentation':
#                     try:
#                         index = ''
#                         address = ''
#                         region_id = ''
#                         type_department_id = ''
#                         type_dep = None
#                         dapartment_present_data = {}
#                         for f in comparison['fields']:
#                             if item["excel_field"] != '' and item["excel_field"] is not None:
#                                 if item["name_field"] == 'address_join':
#                                     addr = parsing_address(debt_exl[f'{item["excel_field"]}'])
#                                     index = addr['index']
#                                     address = addr['address']
#                                 # elif item["name_field"] == 'type_dep':
#                                 #     type_dep = parsing_type_dep(debt_exl[f'{item["excel_field"]}'])
#                                 elif item["name_field"] == 'region_dep':
#                                     region_id = parsing_region_dep(debt_exl[f'{item["excel_field"]}'])
#                                 else:
#                                     dapartment_present_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
#                             else:
#                                 dapartment_present_data[f'{item["name_field"]}'] = ''
#                         dapartment_present_data['address_index'] = index
#                         dapartment_present_data['address'] = address
#                         dapartment_present_data['region'] = region_id
#                         dapartment_present_data['type_department'] = type_dep
#                     except Exception as ex:
#                         # logging.error(ex, exc_info=True)
#                         return Response({"error": f'Ошибка при извлечении данных из excel в модель Lib_Department_Presentation, на строке {count_all}. {ex}'})
#
#                     #             test_data.append(dapartment_present_data)
#                     # return Response({'test_data': test_data, 'count': debtors_count})
#
#
#                     if Lib_Department_Presentation.objects.filter(name=dapartment_present_data['name']).exists():
#                         id_dapartment = Lib_Department_Presentation.objects.get(name=dapartment_present_data['name']).id
#                     else:
#                         id_dapartment = None
#                         upload_log.debug(f"По КД {credits_data['number']}, РОСП ({dapartment_present_data['name']}) не найден")
#
#                 #         try:
#                 #             if dapartment_present_data['name'] is not None and dapartment_present_data['name'] != '':
#                 #                 dapartment_serializers = Lib_Department_PresentationlSerializer(data=dapartment_present_data)
#                 #                 dapartment_serializers.is_valid(raise_exception=True)
#                 #                 obj_dapartment = dapartment_serializers.save()
#                 #                 id_dapartment = obj_dapartment.pk
#                 #
#                 #                 # id_dapartment = count_all
#                 #                 dapartment_present_count += 1
#                 #         except Exception as ex:
#                 #             return Response({"error": f'Ошибка при сохранении в модель Lib_Department_Presentation, на строке {count_all}. {ex}', "dapartment_present_data": dapartment_present_data})
#
#
#                 elif comparison['model']['name_mdl'] == 'Executive_Productions':
#                     try:
#                         num_ep = ''
#                         date_ep = ''
#                         consolidat_ep = ''
#                         pristav = ''
#                         ep_data = {}
#                         comment = ''
#                         for f in comparison['fields']:
#                             if item["excel_field"] != '' and item["excel_field"] is not None:
#                                 if item["name_field"] == 'executive_productions':
#                                     execut_production = parsing_execut_production(debt_exl[f'{item["excel_field"]}'])
#                                     num_ep = execut_production['execut_production']
#                                     date_ep = execut_production['date_ep']
#                                     consolidat_ep = execut_production['consolidat_ep']
#
#                                 elif item["name_field"] == 'curent_debt' or item["name_field"] == 'summa_debt' or item["name_field"] == 'curent_debt' or item["name_field"] == 'gov_toll':
#                                     try:
#                                         summa = debt_exl[f'{item["excel_field"]}']
#                                         ep_data[f'{item["name_field"]}'] = float(summa)
#                                     except:
#                                         ep_data[f'{item["name_field"]}'] = 0
#                                 elif item["name_field"] == 'date_end' or item["name_field"] == 'date_request':
#                                     date_ed = parsing_date_ed(debt_exl[f'{item["excel_field"]}'])
#                                     ep_data[f'{item["name_field"]}'] = date_ed
#                                 elif item["name_field"] == 'pristav':
#                                     pristav = short_str_50(debt_exl[f'{item["excel_field"]}'])
#                                 elif item["name_field"] == 'comment':
#                                     comment = short_str_200(debt_exl[f'{item["excel_field"]}'])
#                                 else:
#                                     ep_data[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
#                             else:
#                                 if item["name_field"] == 'curent_debt' or item["name_field"] == 'summa_debt' or item["name_field"] == 'curent_debt' or item["name_field"] == 'gov_toll':
#                                     ep_data[f'{item["name_field"]}'] = 0
#                                 else:
#                                     ep_data[f'{item["name_field"]}'] = ''
#
#                         # ep_data['number'] = num_ep
#                         # ep_data['date_on'] = date_ep
#                         ep_data['summary_case'] = consolidat_ep
#                         ep_data['pristav'] = pristav
#                         ep_data['rosp'] = id_dapartment
#                         ep_data['executive_document'] = id_ed
#                         ep_data['credit'] = id_credit
#                         ep_data['date_request'] = None
#                         ep_data['comment'] = comment
#                     except Exception as ex:
#                         # logging.error(ex, exc_info=True)
#                         return Response({"error": f'Ошибка при извлечении данных из excel в модель Executive_Productions, на строке {count_all}. {ex}'})
#
#                     #             test_data.append(ep_data)
#                     # return Response({'test_data': test_data, 'count': debtors_count})
#
#                     if Executive_Productions.objects.filter(number=ep_data['number']).exists():
#                         id_ep = Executive_Productions.objects.get(number=ep_data['number']).id
#                     else:
#                         try:
#                             if ep_data['number'] is not None and ep_data['number'] != '':
#                                 ep_serializers = Executive_ProductionsSerializer(data=ep_data)
#                                 ep_serializers.is_valid(raise_exception=True)
#                                 ep_obj = ep_serializers.save()
#                                 id_ep = ep_obj.pk
#                                 ep_count += 1
#                         except Exception as ex:
#                             return Response({"error": f'Ошибка при сохранении в модель Executive_Productions, на строке {count_all}. {ex}', "ep_data": ep_data})
#
#                 # elif comparison['model']['name_mdl'] == 'Collection_Debt':
#                 #     try:
#                 #         collection_debt = {}
#                 #         for f in comparison['fields']:
#                 #             if item["excel_field"] != '' and item["excel_field"] is not None:
#                 #                 if item["name_field"] == 'date_start':
#                 #                     date = parsing_date_ed(debt_exl[f'{item["excel_field"]}'])
#                 #                     collection_debt_exl[f'{item["name_field"]}'] = date
#                 #                 else:
#                 #                     collection_debt_exl[f'{item["name_field"]}'] = debt_exl[f'{item["excel_field"]}']
#                 #             else:
#                 #                 collection_debt_exl[f'{item["name_field"]}'] = ''
#                 #
#                 #         collection_debt_exl['type_department'] = dapartment_present_data['type_department']
#                 #         collection_debt_exl['department_presentation'] = id_dapartment
#                 #         collection_debt_exl['executive_document'] = id_ed
#                 #         collection_debt_exl['credit'] = id_credit
#                 #         collection_debt_exl['reason_cansel'] = None
#                 #         collection_debt_exl['date_return'] = None
#                 #         collection_debt_exl['date_end'] = None
#                 #     except Exception as ex:
#                 #         # logging.error(ex, exc_info=True)
#                 #         return Response({"error": f'Ошибка при извлечении данных из excel в модель Collection_Debt, на строке {count_all}. {ex}'})
#                 #
#                 #     #             test_data.append(collection_debt)
#                 #     # return Response({'test_data': test_data, 'count': debtors_count})
#                 #
#                 #     try:
#                 #         if collection_debt_exl['date_start'] is not None and collection_debt_exl['date_start'] != '':
#                 #             collection_debt_serializers = Collection_DebtSerializer(data=collection_debt)
#                 #             collection_debt_serializers.is_valid(raise_exception=True)
#                 #             collection_debt_serializers.save()
#                 #
#                 #         collection_debt_count += 1
#                 #     except Exception as ex:
#                 #         return Response({"error": f'Ошибка при сохранении в модель Collection_Debt, на строке {count_all}. {ex}', "collection_debt": collection_debt})
#
#
#         return Response({'message': f'Данные успешно сохранены.',
#                          'cessions_count': f'Добавлено {cessions_count} строк Цессий',
#                          'debtors_count': f'Добавлено {debtors_count} строк ФИО должников.',
#                          'credits_count': f'Добавлено {credits_count} строк Кредитов',
#                          'tribunals_count': f'Добавлено {tribunals_count} строк Судов',
#                          'dapartment': f'Добавлено {dapartment_present_count} строк Департаментов предъявления',
#                          'ed_count': f'Добавлено {ed_count} строк ИД',
#                          'ep_count': f'Добавлено {ep_count} строк ИП',
#                          'collection_debt_count': f'Добавлено {collection_debt_count} строк в модель Взыскание долга'})

'''
import_excel и format_data - это вспомогательные методы, для форматирования данных (дата, числа, суммы и т.д.)
format_file.xlsx - это дефолтный файл, который создается при выборе excel файла (из выбранного файла, данные перезаписываются в дефолтный).
И уже дефолтный обрабатывается, и из него данные грузятся в БД.
'''
def import_excel():
    excel_data = pd.read_excel('src/media/data/format_file.xlsx')
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

            # Дату формата дд.мм.гггг привожу к формату гггг-мм-дд
            # datetime.strptime(debtors_data['birthday'], '%Y-%m-%d').date()
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


# def parsing_status_cd(status):
#     try:
#         status_id = Lib_Status_Credit.objects.get(name=status).id
#     except:
#         status_id = Lib_Status_Credit.objects.get(name='Не определен').id
#
#     return status_id


# def parsing_status_ed(status):
#     try:
#         status_id = Lib_Status_ED.objects.get(name=status).id
#     except:
#         status_id = Lib_Status_ED.objects.get(name='Не определен').id
#
#     return status_id


# def parsing_type_ed(type):
#     try:
#         if re.findall(r'(?i)исполнительный\s+лист', type):
#             type = 'Исполнительный лист (бланк)'
#         elif re.findall(r'(?i)судебный\s+приказ', type):
#             type = 'Судебный приказ'
#         type_id = Lib_Type_ED.objects.get(name=type).id
#     except:
#         type_id = Lib_Type_ED.objects.get(name='Не определен').id
#
#     return type_id


# def parsing_claimer_ed(claimer):
#     try:
#         claimer_id = Lib_Claimer_ED.objects.get(name=claimer).id
#     except:
#         claimer_id = Lib_Claimer_ED.objects.get(name='ДИ').id
#
#     return claimer_id


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


def parsing_type_dep(type_dep):
    try:
        pass
        # if re.findall(r'(?i)(Банк)', type_dep):
        #     type_department_id = Lib_Type_Department.objects.get(name='Банк').id
        # elif re.findall(r'(?i)(ПФР)', type_dep):
        #     type_department_id = Lib_Type_Department.objects.get(name='ПФР').id
        # elif re.findall(r'(?i)(ИФНС)', type_dep):
        #     type_department_id = Lib_Type_Department.objects.get(name='ИФНС').id
        # else:
        #     type_department_id = Lib_Type_Department.objects.get(name='РОСП').id
    except:
        type_department_id = None

    return type_department_id


def parsing_region_dep(region):
    try:
        pass
        # region_id = Lib_Regions.objects.get(name=region).id
    except:
        region_id = None

    return region_id


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
    pass

    # path = os.path.join('media/result', 'Реестр для ИФНС')
    #
    # if not os.path.exists(path):
    #     os.mkdir(path)