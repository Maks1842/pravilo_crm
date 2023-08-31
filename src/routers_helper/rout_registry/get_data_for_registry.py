import math
from operator import itemgetter
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.registries.models import registry_headers, registry_structures, registry_filters
from src.debts.models import cession, debtor, credit
from src.collection_debt.models import *

import src.routers_helper.rout_registry.filters as control_filters


# Получить/добавить Наименования столбцов реестров
router_data_registry = APIRouter(
    prefix="/v1/GetDataForRegistry",
    tags=["Registries"]
)


@router_data_registry.get("/")
async def get_data_registry(page: int, filter_id: int, model: str = None, field: str = None, values_filter: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20

    try:
        filter_query = await session.execute(select(registry_filters).where(registry_filters.c.id == filter_id))
        filter_set = filter_query.mappings().fetchone()
        reg_struct_id = int(filter_set['registry_structure_id'])

        reg_struct_query = await session.execute(select(registry_structures.c.items_json).where(registry_structures.c.id == reg_struct_id))
        registry_structur = reg_struct_query.scalar()
        print(f'{filter_set=}')

        # Сортирую список отобранных полей
        list_headers_sort = sorted(registry_structur, key=itemgetter('turn'))

        headers = [{"value": 'actions', "width": 10,}]
        for item in list_headers_sort:
            reg_header_query = await session.execute(select(registry_headers).where(registry_headers.c.id == int(item['id'])))
            reg_header = reg_header_query.mappings().fetchone()
            headers.append({
                "text": reg_header['headers'],
                "value": reg_header['headers_key'],
                "width": reg_header['width_field']})

        values_for_filters = None
        if model:
            query = await session.execute(select(eval(model)).where(getattr(eval(model).c, field) == values_filter))

            queryset = query.mappings().all()
            print(f'{queryset=}')

            values_for_filters = []
            for item_set in queryset:
                if model == 'executive_document':
                    values_for_filters.append(item_set['credit_id'])
                elif model == 'executive_productions':
                    values_for_filters.append(item_set['credit_id'])
                else:
                    values_for_filters.append(item_set['id'])

        if filter_set['function_name'] is None:
            if values_for_filters is None:

                # Извлекаю все КД
                credits_query = await session.execute(select(credit).order_by(credit.c.id).
                                                    limit(per_page).offset((page - 1) * per_page))

                total_credits_query = await session.execute(func.count(distinct(credit.c.number)))
                total_credits = total_credits_query.scalar()
                num_page_all = int(math.ceil(total_credits / per_page))


                summ_credits_query = await session.execute(func.sum(distinct(credit.c.balance_debt)))
                balance_summa = summ_credits_query.scalar()

                statistics = {'total_credits': total_credits,
                          'balance_summa': balance_summa / 100}
            else:
                # Извлекаю КД по фильтрам
                credits_query = await session.execute(select(credit).where(credit.c.id.in_(values_for_filters)).order_by(credit.c.id).
                                                      limit(per_page).offset((page - 1) * per_page))

                total_credits_query = await session.execute(func.count(distinct(credit.c.id.in_(values_for_filters))))
                total_credits = total_credits_query.scalar()
                num_page_all = int(math.ceil(total_credits / per_page))


                summ_credits_query = await session.execute(func.sum(distinct(credit.c.balance_debt)).filter(credit.c.id.in_(values_for_filters)))
                balance_summa = summ_credits_query.scalar()

                statistics = {'total_credits': total_credits,
                          'balance_summa': balance_summa / 100}
        else:
            functions_control = getattr(control_filters, f'{filter_set["function_name"]}')
            credit_id_list = functions_control()

            credits_query = await session.execute(select(credit).where(credit.c.id.in_(credit_id_list)).order_by(credit.c.id).
                                                  limit(per_page).offset((page - 1) * per_page))

            total_credits_query = await session.execute(func.count(distinct(credit.c.id.in_(credit_id_list))))
            total_credits = total_credits_query.scalar()
            num_page_all = int(math.ceil(total_credits / per_page))


            summ_credits_query = await session.execute(func.sum(distinct(credit.c.balance_debt)).filter(credit.c.id.in_(credit_id_list)))
            balance_summa = summ_credits_query.scalar()

            statistics = {'total_credits': total_credits,
                          'balance_summa': balance_summa / 100}

        credits_list = credits_query.mappings().all()
        values_for_registry = calculation_of_filters(registry_structur, credits_list)


        result = {'headers': headers, 'data_debtors': values_for_registry, 'num_page_all': num_page_all, 'statistics': statistics}
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }





async def calculation_of_filters(list_headers, credits_list, session: AsyncSession = Depends(get_async_session)):
    '''
    В данном методе будут извлекаться все данные из всех моделей, с информацией о должниках КД и тд
    Список извлеченных данных сопоставляется с необходимым набором полей для реестра и отправляется на Фронт
    '''
    print('function')
    print(f'session {session}')

    debtor_query = await session.execute(select(debtor))
    print(f'{debtor_query=}')
    debtor_set = debtor_query.mappings().all()
    print(f'{debtor_set=}')

    data_debtors = []
    summa_tribun = 0
    for credit in credits_list:
        passport = ''
        address_registry = ''
        address_resident = ''

        type_ed = ''
        status_ed = ''
        user_ed = ''
        claimer_ed = ''
        tribunal_name = ''
        tribunal_address = ''
        gaspravosudie = 'НЕ возможно'
        ed_null = {
            'number': '',
            'date': '',
            'case_number': '',
            'date_of_receipt_ed': '',
            'date_decision': '',
            'summa_debt_decision': '',
            'state_duty': '',
            'succession': '',
            'marker': '',
            'comment': '',
        }

        reason_end = ''
        rosp_name = ''
        rosp_address = ''
        ep_null = [{
            'number': '',
            'summary_case': '',
            'date_on': '',
            'date_end': '',
            'curent_debt': '',
            'summa_debt': '',
            'gov_toll': '',
            'pristav': '',
            'pristav_phone': '',
            'date_request': '',
            'object_ep': '',
            'claimer': '',
            'comment': ''
        }]

        type_department = ''
        department_presentation = ''
        address_dep_present = ''
        reason_cansel = ''
        collection_debt_null = [{
            'date_start': '',
            'date_return': '',
            'date_end': '',
            'comment': '',
        },]

        tribunal_bankrupt = ''
        financial_manager = ''
        bankrupt_null = [{
            'number_case': '',
            'date_decision': '',
            'date_kommersant': '',
            'date_sale_property': '',
            'date_add_registry': '',
            'date_meeting': '',
        },]

        pay_null = [{
            'summa': '',
            'date': '',
            'payment_doc_num': '',
            'comment': '',
        },]

    #     debtor = Debtors.objects.values().get(pk=credit['debtor_id'])
    #     cession = Cession.objects.values().get(pk=credit['cession_id'])
    #     status_cd = Lib_Status_Credit.objects.values('name').get(pk=credit['status_cd_id'])['name']
    #
    #     if len(debtor['last_name_2']) == 0:
    #         fio = f"{debtor['last_name_1']} {debtor['first_name_1']} {debtor['second_name_1'] or ''}"
    #     else:
    #         fio = f"{debtor['last_name_1']} {debtor['first_name_1']} {debtor['second_name_1'] or ''}" \
    #               f"({debtor['last_name_2']} {debtor['first_name_2']} {debtor['second_name_2'] or ''})"
    #
    #     if debtor['passport_num'] is not None and debtor['passport_num'] != '':
    #         try:
    #             passport_date = datetime.strptime(str(debtor['passport_date']), '%Y-%m-%d').strftime("%d.%m.%Y")
    #         except:
    #             passport_date = ''
    #         passport = f"{debtor['passport_series']} {debtor['passport_num']} от {passport_date}"
    #     if debtor['address_1'] is not None and debtor['address_1'] != '':
    #         address_registry = f"{debtor['index_add_1']  or ''}, {debtor['address_1']  or ''}"
    #     if debtor['address_2'] is not None and debtor['address_2'] != '':
    #         address_resident = f"{debtor['index_add_2']  or ''}, {debtor['address_2']  or ''}"
    #
    #     try:
    #         ed = Executive_Documents.objects.values().get(credit=credit['id'])
    #         if ed['type_ed_id'] is not None and ed['type_ed_id'] != '':
    #             type_ed = Lib_Type_ED.objects.values('name').get(pk=ed['type_ed_id'])['name']
    #         if ed['status_ed_id'] is not None and ed['status_ed_id'] != '':
    #             status_ed = Lib_Status_ED.objects.values('name').get(pk=ed['status_ed_id'])['name']
    #         if ed['user_id'] is not None and ed['user_id'] != '':
    #             user = User.objects.values().get(pk=ed['user_id'])
    #             user_ed = f'{user["first_name"]} {user["last_name"] or ""}'
    #         if ed['claimer_ed_id'] is not None and ed['claimer_ed_id'] != '':
    #             claimer_ed = Lib_Claimer_ED.objects.values('name').get(pk=ed['claimer_ed_id'])['name']
    #         if ed['tribunal_id'] is not None and ed['tribunal_id'] != '':
    #             tribunal = Lib_Tribunals.objects.values().get(pk=ed['tribunal_id'])
    #             tribunal_name = tribunal['name']
    #             tribunal_address = tribunal['address']
    #             if tribunal['gaspravosudie'] == True:
    #                 gaspravosudie = 'Возможно'
    #         if ed['summa_debt_decision'] is not None and ed['summa_debt_decision'] != '':
    #             summa_tribun += ed['summa_debt_decision']
    #             # summa_debt_decision += 1
    #     except:
    #         ed = ed_null
    #
    #     try:
    #         ep = Executive_Productions.objects.values().filter(executive_document=ed['id']).order_by('-date_on')
    #         if ep[0]['reason_end_id'] is not None and ep[0]['reason_end_id'] != '':
    #             reason_end = Lib_Reason_End_EP.objects.values('name').get(pk=ep[0]['reason_end_id'])['name']
    #         if ep[0]['rosp_id'] is not None and ep[0]['rosp_id'] != '':
    #             rosp = Lib_Department_Presentation.objects.values().get(pk=ep[0]['rosp_id'])
    #             rosp_name = rosp['name']
    #             rosp_address = f"{rosp['address_index']  or ''}, {rosp['address']  or ''}"
    #     except:
    #         ep = ep_null
    #
    #     try:
    #         collection_debt = Collection_Debt.objects.values().filter(credit=credit['id']).order_by('-date_start')
    #         if collection_debt[0]['type_department_id'] is not None and collection_debt[0]['type_department_id'] != '':
    #             type_department = Lib_Type_Department.objects.values('name').get(pk=collection_debt[0]['type_department_id'])['name']
    #         if collection_debt[0]['department_presentation_id'] is not None and collection_debt[0]['department_presentation_id'] != '':
    #             department_set = Lib_Department_Presentation.objects.values().get(pk=collection_debt[0]['department_presentation_id'])
    #             department_presentation = department_set['name']
    #             address_dep_present = f"{department_set['address_index'] or ''}, {department_set['address'] or ''}"
    #
    #         if collection_debt[0]['reason_cansel_id']is not None and collection_debt[0]['reason_cansel_id'] != '':
    #             reason_cansel = Lib_Reason_Cansel.objects.values('name').get(pk=collection_debt[0]['reason_cansel_id'])['name']
    #     except:
    #         collection_debt = collection_debt_null
    #
    #     try:
    #         bankrupt = Bankrupt_Cases.objects.values().get(credit=credit['id'])
    #         if bankrupt['tribunal_id'] is not None and bankrupt['tribunal_id'] != '':
    #             tribunal_bankrupt = Lib_Tribunals.objects.values('name').get(pk=bankrupt['tribunal_id'])['name']
    #         if bankrupt['financial_manager_id'] is not None and bankrupt['financial_manager_id'] != '':
    #             financial_manager = Lib_Financial_Manager.objects.values('name').get(pk=bankrupt['financial_manager_id'])['name']
    #     except:
    #         bankrupt = bankrupt_null
    #
    #     try:
    #         pay = Payments.objects.values().filter(credit=credit['id']).order_by('-date')
    #     except:
    #         pay = pay_null
    #
    #     data_items = {'credit_id': credit['id'], 'debtor_id': debtor['id']}
    #     for item in list_headers:
    #         if item['model'] == 'Credits':
    #             if item['headers_key'] == 'status_cd':
    #                 data_items[item['headers_key']] = status_cd
    #             else:
    #                 data_items[item['headers_key']] = credit[f"{item['name_field']}"]
    #
    #         elif item['model'] == 'Debtors':
    #             if item['headers_key'] == 'fio_debtor':
    #                 data_items[item['headers_key']] = fio
    #             elif item['headers_key'] == 'passport':
    #                 data_items[item['headers_key']] = passport
    #             elif item['headers_key'] == 'address_registry':
    #                 data_items[item['headers_key']] = address_registry
    #             elif item['headers_key'] == 'address_resident':
    #                 data_items[item['headers_key']] = address_resident
    #             else:
    #                 data_items[item['headers_key']] = debtor[f"{item['name_field']}"]
    #
    #         elif item['model'] == 'Cession':
    #             data_items[item['headers_key']] = cession[f"{item['name_field']}"]
    #
    #         elif item['model'] == 'Executive_Documents':
    #             if item['headers_key'] == 'type_ed':
    #                 data_items[item['headers_key']] = type_ed
    #             elif item['headers_key'] == 'status_ed':
    #                 data_items[item['headers_key']] = status_ed
    #             elif item['headers_key'] == 'user':
    #                 data_items[item['headers_key']] = user_ed
    #             elif item['headers_key'] == 'claimer_ed':
    #                 data_items[item['headers_key']] = claimer_ed
    #             elif item['headers_key'] == 'tribunal_name_ed':
    #                 data_items[item['headers_key']] = tribunal_name
    #             elif item['headers_key'] == 'tribunal_address_ed':
    #                 data_items[item['headers_key']] = tribunal_address
    #             elif item['headers_key'] == 'gaspravosudie':
    #                 data_items[item['headers_key']] = gaspravosudie
    #             else:
    #                 data_items[item['headers_key']] = ed[f"{item['name_field']}"]
    #
    #         elif item['model'] == 'Executive_Productions':
    #             if item['headers_key'] == 'reason_end_ep':
    #                 data_items[item['headers_key']] = reason_end
    #             elif item['headers_key'] == 'rosp_ep':
    #                 data_items[item['headers_key']] = rosp_name
    #             elif item['headers_key'] == 'address_rosp_ep':
    #                 data_items[item['headers_key']] = rosp_address
    #             else:
    #                 data_items[item['headers_key']] = ep[0][f"{item['name_field']}"]
    #
    #         elif item['model'] == 'Collection_Debt':
    #             if item['headers_key'] == 'type_department_coll':
    #                 data_items[item['headers_key']] = type_department
    #             elif item['headers_key'] == 'dep_present_coll':
    #                 data_items[item['headers_key']] = department_presentation
    #             elif item['headers_key'] == 'add_dep_present_coll':
    #                 data_items[item['headers_key']] = address_dep_present
    #             elif item['headers_key'] == 'reason_cansel_coll':
    #                 data_items[item['headers_key']] = reason_cansel
    #             else:
    #                 try:
    #                     data_items[item['headers_key']] = collection_debt[0][f"{item['name_field']}"]
    #                 except:
    #                     pass
    #
    #         elif item['model'] == 'Bankrupt_Cases':
    #             if item['headers_key'] == 'tribunal_bankrupt':
    #                 data_items[item['headers_key']] = tribunal_bankrupt
    #             elif item['headers_key'] == 'financial_manager_bankrupt':
    #                 data_items[item['headers_key']] = financial_manager
    #             else:
    #                 try:
    #                     data_items[item['headers_key']] = bankrupt[f"{item['name_field']}"]
    #                 except:
    #                     pass
    #
    #         elif item['model'] == 'Payments':
    #             try:
    #                 data_items[item['headers_key']] = pay[0][f"{item['name_field']}"]
    #             except:
    #                 pass
    #
    #     data_debtors.append(data_items)
    #
    # result = {'data_debtors': data_debtors, 'summa_tribun': summa_tribun}
    #
    # return result