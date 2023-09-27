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
from src.references.models import ref_status_credit, ref_result_statement
from src.legal_work.models import legal_work
from src.payments.models import payment

import src.routers_helper.rout_registry.filters as control_filters
from inspect import getmembers, isfunction



# Получить название функций Фильтров
router_func_filters = APIRouter(
    prefix="/v1/GetFunctionsFilters",
    tags=["Registries"]
)


@router_func_filters.get("/")
def get_functions_filters():

    functions_set = getmembers(control_filters, isfunction)

    functions_list = []
    for f in functions_set:
        functions_list.append({'function_name': f[0]})

    return functions_list


# Получить Данные о долгах для реестров
router_data_registry = APIRouter(
    prefix="/v1/GetDataForRegistry",
    tags=["Registries"]
)


@router_data_registry.get("/")
async def get_data_registry(page: int, filter_id: int, model: str = None, field: str = None, values_filter: str = None, session: AsyncSession = Depends(get_async_session)):

    per_page = 20
    legal_number = None

    try:
        filter_query = await session.execute(select(registry_filters).where(registry_filters.c.id == filter_id))
        filter_set = filter_query.mappings().fetchone()
        reg_struct_id: int = filter_set.registry_structure_id

        reg_struct_query = await session.execute(select(registry_structures.c.items_json).where(registry_structures.c.id == reg_struct_id))
        registry_structur = reg_struct_query.scalar()

        # Сортирую список отобранных полей
        list_headers_sort = sorted(registry_structur, key=itemgetter('turn'))

        headers = [{"value": 'actions', "width": 10,}]
        for item in list_headers_sort:
            reg_header_query = await session.execute(select(registry_headers).where(registry_headers.c.id == int(item['id'])))
            reg_header = reg_header_query.mappings().fetchone()
            headers.append({
                "text": reg_header.headers,
                "value": reg_header.headers_key,
                "width": reg_header.width_field})

        values_for_filters = None
        if model:
            query = await session.execute(select(eval(model)).where(getattr(eval(model).c, field) == values_filter))
            queryset = query.mappings().all()

            values_for_filters = []
            for item_set in queryset:
                if model == 'executive_document':
                    values_for_filters.append(item_set.credit_id)
                elif model == 'executive_productions':
                    values_for_filters.append(item_set.credit_id)
                else:
                    values_for_filters.append(item_set.id)

        if filter_set.function_name is None:
            if values_for_filters is None:

                # Извлекаю все КД
                credits_query = await session.execute(select(credit).order_by(credit.c.id).
                                                    limit(per_page).offset((page - 1) * per_page))

                total_credits_query = await session.execute(func.count(distinct(credit.c.number)))
                total_credits = total_credits_query.scalar()
                num_page_all = int(math.ceil(total_credits / per_page))


                summ_credits_query = await session.execute(func.sum(distinct(credit.c.balance_debt)))
                balance_summa = summ_credits_query.scalar()

                if balance_summa is not None:
                    balance_summa = balance_summa / 100

                statistics = {'total_credits': total_credits,
                          'balance_summa': balance_summa}
            else:
                # Извлекаю КД по фильтрам
                credits_query = await session.execute(select(credit).where(credit.c.id.in_(values_for_filters)).order_by(credit.c.id).
                                                      limit(per_page).offset((page - 1) * per_page))

                total_credits_query = await session.execute(func.count(distinct(credit.c.id.in_(values_for_filters))))
                total_credits = total_credits_query.scalar()
                num_page_all = int(math.ceil(total_credits / per_page))


                summ_credits_query = await session.execute(func.sum(distinct(credit.c.balance_debt)).filter(credit.c.id.in_(values_for_filters)))
                balance_summa = summ_credits_query.scalar()

                if balance_summa is not None:
                    balance_summa = balance_summa / 100

                statistics = {'total_credits': total_credits,
                          'balance_summa': balance_summa}
        else:
            functions_control = getattr(control_filters, f'{filter_set.function_name}')
            credit_id_list = functions_control()

            credits_query = await session.execute(select(credit).where(credit.c.id.in_(credit_id_list)).order_by(credit.c.id).
                                                  limit(per_page).offset((page - 1) * per_page))

            total_credits_query = await session.execute(func.count(distinct(credit.c.id.in_(credit_id_list))))
            total_credits = total_credits_query.scalar()
            num_page_all = int(math.ceil(total_credits / per_page))


            summ_credits_query = await session.execute(func.sum(distinct(credit.c.balance_debt)).filter(credit.c.id.in_(credit_id_list)))
            balance_summa = summ_credits_query.scalar()

            if balance_summa is not None:
                balance_summa = balance_summa / 100

            statistics = {'total_credits': total_credits,
                          'balance_summa': balance_summa}

        credits_list = credits_query.mappings().all()
        values_for_registry = await calculation_of_filters(registry_structur, credits_list, legal_number, session)


        result = {'headers': headers, 'data_debtors': values_for_registry, 'num_page_all': num_page_all, 'statistics': statistics}
        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


async def calculation_of_filters(list_headers, credits_list, legal_number, session):
    '''
    В данном методе будут извлекаться все данные из всех моделей, с информацией о должниках КД и тд
    Список извлеченных данных сопоставляется с необходимым набором полей для реестра и отправляется на Фронт
    '''

    data_debtors = []
    summa_tribun_all = 0
    for credit_item in credits_list:
        summa_cessii = 0
        date_cessii = ''
        summa_by_cession = 0
        credit_summa = 0
        overdue_od = 0
        percent_of_od = 0
        balance_debt = 0
        credit_date_start = ''
        summa_tribun = 0
        summa_pay = 0

        passport = ''
        birthday = ''
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
        ep_null = {
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
        }

        result_1 = ''
        legal_null = {
            'legal_number': '',
        }

        pay_null = {
            'summa': '',
            'date': '',
            'payment_doc_num': '',
            'comment': '',
        }

        debtor_query = await session.execute(select(debtor).where(debtor.c.id == int(credit_item['debtor_id'])))
        debtor_item = debtor_query.mappings().fetchone()

        cession_query = await session.execute(select(cession).where(cession.c.id == int(credit_item['cession_id'])))
        cession_item = cession_query.mappings().fetchone()

        status_cd_query = await session.execute(select(ref_status_credit.c.name).where(ref_status_credit.c.id == int(credit_item['status_cd_id'])))
        status_cd = status_cd_query.scalar()

        if cession_item['summa'] is not None:
            summa_cessii = cession_item['summa'] / 100
        if cession_item['date'] is not None:
            try:
                date_cessii = datetime.strptime(str(cession_item['date']), '%Y-%m-%d').strftime("%d.%m.%Y")
            except:
                pass

        if credit_item['summa_by_cession'] is not None:
            summa_by_cession = credit_item['summa_by_cession'] / 100
        if credit_item['summa'] is not None:
            credit_summa = credit_item['summa'] / 100
        if credit_item['overdue_od'] is not None:
            overdue_od = credit_item['overdue_od'] / 100
        if credit_item['percent_of_od'] is not None:
            percent_of_od = credit_item['percent_of_od'] / 100
        if credit_item['balance_debt'] is not None:
            balance_debt = credit_item['balance_debt'] / 100
        if credit_item['date_start'] is not None:
            try:
                credit_date_start = datetime.strptime(str(credit_item['date_start']), '%Y-%m-%d').strftime("%d.%m.%Y")
            except:
                pass

        if debtor_item.last_name_2 is not None:
            fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                         f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
        else:
            fio = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"
        if debtor_item.birthday is not None:
            try:
                birthday = datetime.strptime(str(debtor_item.birthday), '%Y-%m-%d').strftime("%d.%m.%Y")
            except:
                pass

        if debtor_item.passport_num is not None:
            try:
                passport_date = datetime.strptime(str(debtor_item.passport_date), '%Y-%m-%d').strftime("%d.%m.%Y")
            except:
                passport_date = ''
            passport = f"{debtor_item.passport_series} {debtor_item.passport_num} от {passport_date}"
        if debtor_item.address_1 is not None:
            address_registry = f"{debtor_item.index_add_1  or ''}, {debtor_item.address_1  or ''}"
        if debtor_item.address_2 is not None:
            address_resident = f"{debtor_item.index_add_2  or ''}, {debtor_item.address_2  or ''}"
        if debtor_item.tribunal_id is not None:
            tribunal_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == int(debtor_item.tribunal_id)))
            tribunal_item = tribunal_query.mappings().fetchone()
            tribunal_name = tribunal_item.name
            tribunal_address = tribunal_item.address
            if tribunal_item.gaspravosudie:
                gaspravosudie = 'Возможно'

        try:
            ed_query = await session.execute(select(executive_document).where(executive_document.c.credit_id == int(credit_item['id'])).
                                             order_by(desc(executive_document.c.id)))
            ed_item = ed_query.mappings().fetchone()
            if ed_item.type_ed_id is not None:
                type_ed_query = await session.execute(select(ref_type_ed.c.name).where(ref_type_ed.c.id == int(ed_item.type_ed_id)))
                type_ed = type_ed_query.scalar()
            if ed_item.status_ed_id is not None:
                status_ed_query = await session.execute(select(ref_status_ed.c.name).where(ref_status_ed.c.id == int(ed_item.status_ed_id)))
                status_ed = status_ed_query.scalar()
            if ed_item.user_id is not None:
                user_query = await session.execute(select(user).where(user.c.id == int(ed_item.user_id)))
                user_item = user_query.mappings().fetchone()
                user_ed = f'{user_item["first_name"]} {user_item["last_name"] or ""}'
            if ed_item.claimer_ed_id is not None:
                claimer_ed_query = await session.execute(select(ref_claimer_ed.c.name).where(ref_claimer_ed.c.id == int(ed_item.claimer_ed_id)))
                claimer_ed = claimer_ed_query.scalar()
            if ed_item.tribunal_id is not None:
                tribunal_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == int(ed_item.tribunal_id)))
                tribunal_item = tribunal_query.mappings().fetchone()
                tribunal_name = tribunal_item.name
                tribunal_address = tribunal_item.address
                # if tribunal_item.gaspravosudie == True:
                #     gaspravosudie = 'Возможно'
            if ed_item.summa_debt_decision is not None:
                summa_tribun = ed_item.summa_debt_decision / 100
                summa_tribun_all += summa_tribun
        except:
            ed_item = ed_null

        try:
            ep_query = await session.execute(select(executive_productions).where(executive_productions.c.executive_document_id == int(ed_item['id'])).
                                             order_by(desc(executive_productions.c.date_on)))
            ep_item = ep_query.mappings().fetchone()
            if ep_item.reason_end_id is not None:
                reason_end_query = await session.execute(select(ref_reason_end_ep.c.name).where(ref_reason_end_ep.c.id == int(ep_item.reason_end_id)))
                reason_end = reason_end_query.scalar()
            if ep_item.rosp_id is not None:
                rosp_query = await session.execute(select(ref_rosp).where(ref_rosp.c.id == int(ep_item.rosp_id)))
                rosp = rosp_query.mappings().fetchone()
                rosp_name = rosp.name
                rosp_address = f"{rosp.address_index  or ''}, {rosp.address  or ''}"
        except:
            ep_item = ep_null

        if legal_number:
            try:
                legal_work_query = await session.execute(select(legal_work).where(legal_work.c.legal_number == str(legal_number)))
                legal_work_item = legal_work_query.mappings().fetchone()
                if legal_work_item.result_1_id is not None:
                    result_statement_query = await session.execute(select(ref_result_statement.c.name).where(ref_result_statement.c.id == int(legal_work_item.result_1_id)))
                    result_1 = result_statement_query.scalar()
            except:
                legal_work_item = legal_null
        else:
            legal_work_item = legal_null

        try:
            pay_query = await session.execute(select(payment).where(payment.c.credit_id == int(credit_item['id'])).
                                              order_by(desc(payment.c.date)))
            pay_item = pay_query.mappings().fetchone()

            if pay_item.summa is not None:
                summa_pay = pay_item.summa / 100
        except:
            pay_item = pay_null

        data_items = {'credit_id': credit_item['id'], 'debtor_id': debtor_item['id']}
        for item in list_headers:
            if item['model'] == 'credit':
                if item['headers_key'] == 'status_cd':
                    data_items[item['headers_key']] = status_cd
                elif item['headers_key'] == 'summa_by_cession':
                    data_items[item['headers_key']] = summa_by_cession
                elif item['headers_key'] == 'summa_cd':
                    data_items[item['headers_key']] = credit_summa
                elif item['headers_key'] == 'overdue_od':
                    data_items[item['headers_key']] = overdue_od
                elif item['headers_key'] == 'percent_of_od':
                    data_items[item['headers_key']] = percent_of_od
                elif item['headers_key'] == 'balance_debt':
                    data_items[item['headers_key']] = balance_debt
                elif item['headers_key'] == 'date_start_cd':
                    data_items[item['headers_key']] = credit_date_start
                else:
                    data_items[item['headers_key']] = credit_item[f"{item['name_field']}"]

            elif item['model'] == 'debtor':
                if item['headers_key'] == 'fio_debtor':
                    data_items[item['headers_key']] = fio
                elif item['headers_key'] == 'birthday':
                    data_items[item['headers_key']] = birthday
                elif item['headers_key'] == 'passport':
                    data_items[item['headers_key']] = passport
                elif item['headers_key'] == 'address_registry':
                    data_items[item['headers_key']] = address_registry
                elif item['headers_key'] == 'address_resident':
                    data_items[item['headers_key']] = address_resident
                else:
                    data_items[item['headers_key']] = debtor_item[f"{item['name_field']}"]

            elif item['model'] == 'cession':
                if item['headers_key'] == 'summa_cessii':
                    data_items[item['headers_key']] = summa_cessii
                elif item['headers_key'] == 'date_cessii':
                    data_items[item['headers_key']] = date_cessii
                else:
                    data_items[item['headers_key']] = cession_item[f"{item['name_field']}"]

            elif item['model'] == 'executive_document':
                if item['headers_key'] == 'type_ed':
                    data_items[item['headers_key']] = type_ed
                elif item['headers_key'] == 'status_ed':
                    data_items[item['headers_key']] = status_ed
                elif item['headers_key'] == 'user_ed':
                    data_items[item['headers_key']] = user_ed
                elif item['headers_key'] == 'claimer_ed':
                    data_items[item['headers_key']] = claimer_ed
                elif item['headers_key'] == 'tribunal_name_ed':
                    data_items[item['headers_key']] = tribunal_name
                elif item['headers_key'] == 'tribunal_address_ed':
                    data_items[item['headers_key']] = tribunal_address
                elif item['headers_key'] == 'summa_debt_decision_ed':
                    data_items[item['headers_key']] = summa_tribun
                else:
                    try:
                        data_items[item['headers_key']] = ed_item[f"{item['name_field']}"]
                    except:
                        pass

            elif item['model'] == 'executive_productions':
                if item['headers_key'] == 'reason_end_ep':
                    data_items[item['headers_key']] = reason_end
                elif item['headers_key'] == 'rosp_ep':
                    data_items[item['headers_key']] = rosp_name
                elif item['headers_key'] == 'address_rosp_ep':
                    data_items[item['headers_key']] = rosp_address
                else:
                    data_items[item['headers_key']] = ep_item[f"{item['name_field']}"]

            elif item['model'] == 'legal_work':
                if item['headers_key'] == 'result_1_legal':
                    data_items[item['headers_key']] = result_1
                else:
                    data_items[item['headers_key']] = legal_work_item[f"{item['name_field']}"]

            elif item['model'] == 'payment':
                if item['headers_key'] == 'summa_last_payment':
                    data_items[item['headers_key']] = summa_pay
                else:
                    data_items[item['headers_key']] = pay_item[f"{item['name_field']}"]

            elif item['model'] == 'ref_tribunal':
                if item['headers_key'] == 'gaspravosudie':
                    data_items[item['headers_key']] = gaspravosudie
                elif item['headers_key'] == 'tribunal_name':
                    data_items[item['headers_key']] = tribunal_name
                elif item['headers_key'] == 'tribunal_address':
                    data_items[item['headers_key']] = tribunal_address

        data_debtors.append(data_items)

    result = {'data_debtors': data_debtors, 'summa_tribun_all': summa_tribun_all}

    return result