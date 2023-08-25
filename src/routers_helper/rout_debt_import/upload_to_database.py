import pandas as pd
import json
from datetime import datetime, date
import re
from src.routers_helper.rout_debt_import.re_pattern_for_excel import RePattern

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.registries.models import registry_headers, registry_structures

'''
НЕОБХОДИМО НАСТРАИВАТЬ ПОД КАЖДЫЙ НОВЫЙ РЕЕСТР


Импорт данных из файлов Excel.
Извлеченные данные попадают на фронтенд, где происходит сопоставление наименований извлеченных заголовков столбцов
с имеющимися полями в DataBase.
С фронта 'csv_field' приходят в виде индексов, которые на бэке изменяются на фактические названия полей Excel.
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

    # Сопоставление полей Модели с csv_field, и изменение индексов на фактическое наименование
    # for csv in comparison_excel_to_db:
    #     for f in csv['fields']:
    #         for h in headersCSV:
    #             if f['csv_field'] == h['value']:
    #                 f['csv_field'] = h['text']
#
#         count_all = 0
#         debtors_count = 0
#         cessions_count = 0
#         credits_count = 0
#         tribunals_count = 0
#         dapartment_present_count = 0
#         ed_count = 0
#         ep_count = 0
#         collection_debt_count = 0
#
#         test_data = []
#
#         # Сопоставление полей "Поле БД": debt["заголовок из excel"]
#         for debt in registry_csv:
#             count_all += 1
#
#             for comparison in comparison_csv_json:
#
#                 id_dapartment = None
#                 id_ed = None
#
#
#                 #         test_data.append(comparison)
#                 # return Response({'test_data': test_data, 'count': debtors_count})
#                 if comparison['model']['name_mdl'] == 'Debtors':
#                     # test_data.append(debt[f'{comparison["fields"][0]["csv_field"]}'])
#                     try:
#                         debtors_data = {}
#                         last_name_1 = ''
#                         first_name_1 = ''
#                         second_name_1 = ''
#                         last_name_2 = ''
#                         first_name_2 = ''
#                         second_name_2 = ''
#                         passport_series = ''
#                         passport_num = ''
#                         passport_date = ''
#                         passport_department = ''
#                         index_1 = ''
#                         address_1 = ''
#                         index_2 = ''
#                         address_2 = ''
#                         comment = ''
#                         inn = ''
#                         for f in comparison['fields']:
#                             if f["csv_field"] != '' and f["csv_field"] is not None:
#                                 if f["name"] == 'fio':
#                                     fio = parsing_fio(debt[f'{f["csv_field"]}'])
#                                     last_name_1 = fio['last_name_1']
#                                     first_name_1 = fio['first_name_1']
#                                     second_name_1 = fio['second_name_1']
#                                     last_name_2 = fio['last_name_2']
#                                     first_name_2 = fio['first_name_2']
#                                     second_name_2 = fio['second_name_2']
#
#                                     debtors_data['last_name_1'] = last_name_1
#                                     debtors_data['first_name_1'] = first_name_1
#                                     debtors_data['second_name_1'] = second_name_1
#                                     debtors_data['last_name_2'] = last_name_2
#                                     debtors_data['first_name_2'] = first_name_2
#                                     debtors_data['second_name_2'] = second_name_2
#
#                                 elif f["name"] == 'passport':
#                                     passport = parsing_passport(debt[f'{f["csv_field"]}'])
#                                     passport_series = passport['passport_series']
#                                     passport_num = passport['passport_num']
#                                     passport_date = passport['passport_date']
#                                     passport_department = passport['passport_department']
#
#                                 elif f["name"] == 'address_1':
#                                     addr = parsing_address(debt[f'{f["csv_field"]}'])
#                                     index_1 = addr['index']
#                                     address_1 = addr['address']
#
#                                 elif f["name"] == 'address_2':
#                                     addr = parsing_address(debt[f'{f["csv_field"]}'])
#                                     index_2 = addr['index']
#                                     address_2 = addr['address']
#
#                                 elif f["name"] == 'comment':
#                                     comment = short_str_200(debt[f'{f["csv_field"]}'])
#                                     debtors_data['comment'] = comment
#
#                                 elif f["name"] == 'inn':
#                                     inn = format_inn(debt[f'{f["csv_field"]}'])
#                                     debtors_data['inn'] = inn
#
#                                 else:
#                                     debtors_data[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                             else:
#                                 debtors_data[f'{f["name"]}'] = ''
#
#
#                             debtors_data['passport_series'] = passport_series
#                             debtors_data['passport_num'] = passport_num
#                             # debtors_data['passport_date'] = passport_date
#                             # debtors_data['passport_department'] = passport_department
#                             debtors_data['index_add_1'] = index_1
#                             debtors_data['address_1'] = address_1
#                             debtors_data['index_add_2'] = index_2
#                             debtors_data['address_2'] = address_2
#
#
#                     except Exception as ex:
#                         return Response({"error": f'Ошибка при извлечении данных из excel в модель Debtors, на строке {count_all}. {ex}'})
#
#
#                     #             test_data.append(debtors_data)
#                     # return Response({'test_data': test_data, 'count': debtors_count})
#
#
#                     if Debtors.objects.filter(last_name_1=debtors_data['last_name_1'], first_name_1=debtors_data['first_name_1'],
#                                               second_name_1=debtors_data['second_name_1'], birthday=debtors_data['birthday']).exists():
#                         id_debtor = Debtors.objects.filter(last_name_1=debtors_data['last_name_1'], first_name_1=debtors_data['first_name_1'],
#                                                            second_name_1=debtors_data['second_name_1']).get(birthday=debtors_data['birthday']).id
#                     elif Debtors.objects.filter(last_name_1=debtors_data['last_name_1'], first_name_1=debtors_data['first_name_1'], birthday=debtors_data['birthday']).exists():
#                         id_debtor = Debtors.objects.filter(last_name_1=debtors_data['last_name_1'], first_name_1=debtors_data['first_name_1']).get(birthday=debtors_data['birthday']).id
#
#                     else:
#                         try:
#                             debtor_serializers = DebtorsSerializer(data=debtors_data)
#                             debtor_serializers.is_valid(raise_exception=True)
#                             obj_debtor = debtor_serializers.save()
#                             id_debtor = obj_debtor.pk
#
#                             #test
#                             # id_debtor = count_all
#
#                             debtors_count += 1
#                         except Exception as ex:
#                             return Response({"error": f'Ошибка при сохранении в модель Debtors, на строке {count_all}. {ex}', "debtors_data": debtors_data})
#
#                 elif comparison['model']['name_mdl'] == 'Cession':
#                     try:
#                         cessions_data = {}
#                         for f in comparison['fields']:
#                             if f["csv_field"] != '' and f["csv_field"] is not None:
#                                 if f["name"] == 'summa':
#                                     try:
#                                         summa = debt[f'{f["csv_field"]}']
#                                         cessions_data[f'{f["name"]}'] = float(summa)
#                                     except:
#                                         cessions_data[f'{f["name"]}'] = 0
#                                 elif f["name"] == 'date':
#                                     date_ed = parsing_date_ed(debt[f'{f["csv_field"]}'])
#                                     cessions_data[f'{f["name"]}'] = date_ed
#                                 else:
#                                     cessions_data[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                             else:
#                                 cessions_data[f'{f["name"]}'] = ''
#                     except Exception as ex:
#                         return Response({"error": f'Ошибка при извлечении данных из excel в модель Cession, на строке {count_all}. {ex}'})
#
#                     #             test_data.append(cessions_data)
#                     # return Response({'test_data': test_data, 'count': debtors_count})
#
#                     if Cession.objects.filter(name=cessions_data['name'], number=cessions_data['number']).exists():
#                         id_cession = Cession.objects.filter(name=cessions_data['name']).get(number=cessions_data['number']).id
#                     else:
#                         try:
#                             cession_serializers = CessionSerializer(data=cessions_data)
#                             cession_serializers.is_valid(raise_exception=True)
#                             obj_cession = cession_serializers.save()
#                             id_cession = obj_cession.pk
#
#                             #test
#                             # id_cession = count_all
#
#                             cessions_count += 1
#                         except Exception as ex:
#                             return Response({"error": f'Ошибка при сохранении в модель Cession, на строке {count_all}. {ex}', "cessions_data": cessions_data})
#
#                 if comparison['model']['name_mdl'] == 'Credits':
#                     try:
#                         credits_data = {}
#                         status_cd_id = 1
#
#                         for f in comparison['fields']:
#                             if f["csv_field"] != '' and f["csv_field"] is not None:
#                                 if f["name"] == 'status_cd':
#                                     status_cd_id = parsing_status_cd(debt[f'{f["csv_field"]}'])
#
#                                 elif f["name"] == 'summa' or f["name"] == 'summa_by_cession' or f["name"] == 'interest_rate' or f["name"] == 'overdue_od' or \
#                                         f["name"] == 'overdue_percent' or f["name"] == 'penalty' or f["name"] == 'percent_of_od' \
#                                         or f["name"] == 'gov_toll' or f["name"] == 'balance_debt':
#                                     try:
#                                         summa = debt[f'{f["csv_field"]}']
#                                         credits_data[f'{f["name"]}'] = float(round(summa, 2))
#                                     except:
#                                         credits_data[f'{f["name"]}'] = 0
#                                 elif f["name"] == 'date_start':
#                                     date_start = parsing_date_start(debt[f'{f["csv_field"]}'])
#                                     credits_data[f'{f["name"]}'] = date_start
#                                 else:
#                                     credits_data[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                             else:
#                                 if f["name"] == 'summa' or f["name"] == 'summa_by_cession' or f["name"] == 'interest_rate' or f["name"] == 'overdue_od' or \
#                                         f["name"] == 'overdue_percent' or f["name"] == 'penalty' or f["name"] == 'percent_of_od' \
#                                         or f["name"] == 'gov_toll' or f["name"] == 'balance_debt':
#                                     credits_data[f'{f["name"]}'] = 0
#                                 else:
#                                     credits_data[f'{f["name"]}'] = ''
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
#                             if f["csv_field"] != '' and f["csv_field"] is not None:
#                                 if f["name"] == 'email':
#                                     email = short_str_100(debt[f'{f["csv_field"]}'])
#                                 else:
#                                     tribunals_data[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                             else:
#                                 tribunals_data[f'{f["name"]}'] = ''
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
#                             if f["csv_field"] != '' and f["csv_field"] is not None:
#                                 if f["name"] == 'type_ed':
#                                     type_ed_id = parsing_type_ed(debt[f'{f["csv_field"]}'])
#                                     type_id = type_ed_id
#                                 elif f["name"] == 'claimer_ed':
#                                     claimer_ed_id = parsing_claimer_ed(debt[f'{f["csv_field"]}'])
#                                     claimer_id = claimer_ed_id
#                                 elif f["name"] == 'number':
#                                     num_ed = short_str_50(debt[f'{f["csv_field"]}'])
#                                 elif f["name"] == 'status_ed':
#                                     status_ed_id = parsing_status_ed(debt[f'{f["csv_field"]}'])
#                                 else:
#                                     if f["name"] == 'summa_debt_decision' or f["name"] == 'state_duty':
#                                         try:
#                                             summa = debt[f'{f["csv_field"]}']
#                                             ed_data[f'{f["name"]}'] = float(round(summa, 2))
#                                         except:
#                                             ed_data[f'{f["name"]}'] = 0
#                                     elif f["name"] == 'date' or f["name"] == 'date_of_receipt_ed' or f["name"] == 'date_decision' or f["name"] == 'succession':
#                                         date_ed = parsing_date_ed(debt[f'{f["csv_field"]}'])
#                                         ed_data[f'{f["name"]}'] = date_ed
#                                     elif f["name"] == 'comment':
#                                         comment = short_str_200(debt[f'{f["csv_field"]}'])
#                                     else:
#                                         ed_data[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                             else:
#                                 if f["name"] == 'summa_debt_decision' or f["name"] == 'state_duty':
#                                     ed_data[f'{f["name"]}'] = 0
#                                 else:
#                                     ed_data[f'{f["name"]}'] = ''
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
#                             if f["csv_field"] != '' and f["csv_field"] is not None:
#                                 if f["name"] == 'address_join':
#                                     addr = parsing_address(debt[f'{f["csv_field"]}'])
#                                     index = addr['index']
#                                     address = addr['address']
#                                 # elif f["name"] == 'type_dep':
#                                 #     type_dep = parsing_type_dep(debt[f'{f["csv_field"]}'])
#                                 elif f["name"] == 'region_dep':
#                                     region_id = parsing_region_dep(debt[f'{f["csv_field"]}'])
#                                 else:
#                                     dapartment_present_data[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                             else:
#                                 dapartment_present_data[f'{f["name"]}'] = ''
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
#                             if f["csv_field"] != '' and f["csv_field"] is not None:
#                                 if f["name"] == 'executive_productions':
#                                     execut_production = parsing_execut_production(debt[f'{f["csv_field"]}'])
#                                     num_ep = execut_production['execut_production']
#                                     date_ep = execut_production['date_ep']
#                                     consolidat_ep = execut_production['consolidat_ep']
#
#                                 elif f["name"] == 'curent_debt' or f["name"] == 'summa_debt' or f["name"] == 'curent_debt' or f["name"] == 'gov_toll':
#                                     try:
#                                         summa = debt[f'{f["csv_field"]}']
#                                         ep_data[f'{f["name"]}'] = float(summa)
#                                     except:
#                                         ep_data[f'{f["name"]}'] = 0
#                                 elif f["name"] == 'date_end' or f["name"] == 'date_request':
#                                     date_ed = parsing_date_ed(debt[f'{f["csv_field"]}'])
#                                     ep_data[f'{f["name"]}'] = date_ed
#                                 elif f["name"] == 'pristav':
#                                     pristav = short_str_50(debt[f'{f["csv_field"]}'])
#                                 elif f["name"] == 'comment':
#                                     comment = short_str_200(debt[f'{f["csv_field"]}'])
#                                 else:
#                                     ep_data[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                             else:
#                                 if f["name"] == 'curent_debt' or f["name"] == 'summa_debt' or f["name"] == 'curent_debt' or f["name"] == 'gov_toll':
#                                     ep_data[f'{f["name"]}'] = 0
#                                 else:
#                                     ep_data[f'{f["name"]}'] = ''
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
#                 #             if f["csv_field"] != '' and f["csv_field"] is not None:
#                 #                 if f["name"] == 'date_start':
#                 #                     date = parsing_date_ed(debt[f'{f["csv_field"]}'])
#                 #                     collection_debt[f'{f["name"]}'] = date
#                 #                 else:
#                 #                     collection_debt[f'{f["name"]}'] = debt[f'{f["csv_field"]}']
#                 #             else:
#                 #                 collection_debt[f'{f["name"]}'] = ''
#                 #
#                 #         collection_debt['type_department'] = dapartment_present_data['type_department']
#                 #         collection_debt['department_presentation'] = id_dapartment
#                 #         collection_debt['executive_document'] = id_ed
#                 #         collection_debt['credit'] = id_credit
#                 #         collection_debt['reason_cansel'] = None
#                 #         collection_debt['date_return'] = None
#                 #         collection_debt['date_end'] = None
#                 #     except Exception as ex:
#                 #         # logging.error(ex, exc_info=True)
#                 #         return Response({"error": f'Ошибка при извлечении данных из excel в модель Collection_Debt, на строке {count_all}. {ex}'})
#                 #
#                 #     #             test_data.append(collection_debt)
#                 #     # return Response({'test_data': test_data, 'count': debtors_count})
#                 #
#                 #     try:
#                 #         if collection_debt['date_start'] is not None and collection_debt['date_start'] != '':
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
            try:
                if re.findall(r'\d{2}\.\d{2}\.\d{4}', x):
                    x = datetime.strptime(x, '%d.%m.%Y').strftime("%Y-%m-%d")
            except:
                pass

            try:
                x = datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f').strftime("%Y-%m-%d")
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
        pass
    return inn


def parsing_fio(fio):

    if "(" in fio:
        fio_1_sp = re.search(RePattern.fio_1, fio).group().strip()
        fio_2_sp = re.search(RePattern.fio_2, fio).group().strip()

        last_name_1 = fio
        first_name_1 = 'ОШИБКА'
        second_name_1 = ''
        last_name_2 = ''
        first_name_2 = ''
        second_name_2 = ''
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
        last_name_2 = ''
        first_name_2 = ''
        second_name_2 = ''

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
        passport_series = ''

    try:
        passport_num = re.search(RePattern.passport_num, passport).group().strip()
    except:
        passport_num = ''

    try:
        passport_dep = re.search(RePattern.passport_department, passport).group().strip()
        passport_department = re.sub(r' \d{2}\.\d{2}\.\d{4}| \d{2}\.\d{2}\.\d{2}', '', passport_dep)
    except:
        passport_department = ''

    try:
        passport_date_re = re.search(RePattern.passport_date, passport).group().strip()
        passport_date = datetime.strptime(passport_date_re, '%d.%m.%Y').strftime("%Y-%m-%d")
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
        index = ''

    try:
        address = re.search(RePattern.address_re, addr).group().strip()
        if len(address) > 200:
            address = address[-200:]
    except:
        address = ''

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
        date_ed = re.search(r'\d{4}-\d{2}-\d{2}', date).group()
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
        execut_production = ''

    try:
        date = re.search(RePattern.date_ep, ep).group().strip()
        date_ep = datetime.strptime(date, '%d.%m.%Y').strftime("%Y-%m-%d")
    except:
        date_ep = None

    try:
        consolidat_ep = re.search(RePattern.consolidat_ep, ep).group().strip()
    except:
        consolidat_ep = ''

    result = {'execut_production': execut_production,
              'date_ep': date_ep,
              'consolidat_ep': consolidat_ep}

    return result