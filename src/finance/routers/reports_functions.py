from sqlalchemy import select, func, distinct, and_, or_, true, false, not_
from src.debts.models import cession, credit
from src.payments.models import payment
from src.finance.models import expenses, ref_expenses_category

from datetime import datetime, timedelta
from variables_for_backend import VarStatusCD


'''
Функция получения суммы выручки(платежей) в разрезе Портфелей(Цессий)
'''
async def get_revenue(data,  session):

    dates = data['dates']
    cession_id = data['cession_id']

    if len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1
    elif len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    if cession_id:
        cession_query = await session.execute(select(cession).where(cession.c.id == int(cession_id)))
    else:
        cession_query = await session.execute(select(cession))

    data_revenue = []
    for item in cession_query.mappings().all():
        cession_id: int = item.id
        cession_name = item.name

        credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
        credits_id_list = credits_id_query.scalars().all()

        if len(credits_id_list) > 0:
            if date_1 == None:
                summa_query = await session.execute(select(func.sum(payment.c.summa)).filter(payment.c.credit_id.in_(credits_id_list)))
            else:
                summa_query = await session.execute(select(func.sum(payment.c.summa)).
                                                    filter(and_(payment.c.date >= date_1, payment.c.date <= date_2, payment.c.credit_id.in_(credits_id_list))))

            summa = summa_query.scalar()

            if summa:
                summa_revenue = round(summa / 100, 2)
            else:
                summa_revenue = 0

            data_revenue.append({
                "cession_id": cession_id,
                "cession_name": cession_name,
                "summa_revenue": summa_revenue,
            })

    return data_revenue


'''
Функция расчета коэффициента(доли) Портфеля в общей структуре
Вес рассчитывается по количеству КД в портфеле
Учитываются только базовые(родительские) КД, производные(дочерние) в расчет не берутся
'''
async def get_coefficient_cession(cession_id: int,  session):

    status_cd = VarStatusCD.status_cd_pgsh

    cession_number_credit_total_query = await session.execute(select(func.count(distinct(credit.c.id)).filter(credit.c.cession_id == cession_id)))

    total_credit_active_query = await session.execute(select(func.count(distinct(credit.c.id)).filter(and_(credit.c.parent_id.is_(None),
                                                                                                    credit.c.status_cd_id != status_cd))))
    total_credit_active = total_credit_active_query.scalar()

    cession_number_credit_active_query = await session.execute(select(func.count(distinct(credit.c.id)).filter(and_(credit.c.cession_id == cession_id,
                                                                                                             credit.c.parent_id.is_(None),
                                                                                                             credit.c.status_cd_id != status_cd))))
    cession_number_credit_total = cession_number_credit_total_query.scalar()
    cession_number_credit_active = cession_number_credit_active_query.scalar()

    coefficient_cession = round(cession_number_credit_active / total_credit_active, 2)

    result = {
        'cession_number_credit_total': cession_number_credit_total,
        'cession_number_credit_active': cession_number_credit_active,
        'coefficient_cession': coefficient_cession
    }

    return result


'''
Функция получения суммы расходов в разрезе Портфелей(Цессий).
Расходы с идентификатором cession_id покрываются за счет доходов данного портфеля,
если нет идентификатора cession_id, то расходы рассчитываются пропорционально долям Портфелей.
Результат выводится в разрезе категорий расходов.
'''
async def get_expenses_cession(data,  session):

    dates = data['dates']
    cession_id = data['cession_id']

    if len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1
    elif len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    if cession_id:
        cession_query = await session.execute(select(cession).where(cession.c.id == int(cession_id)))
    else:
        cession_query = await session.execute(select(cession))

    expenses_category_query = await session.execute(select(ref_expenses_category))
    expenses_category = expenses_category_query.mappings().all()

    cession_expenses = []
    for item in cession_query.mappings().all():
        cession_id: int = item.id
        cession_name = item.name

        data_coefficient = await get_coefficient_cession(cession_id,  session)
        coefficient_cession = data_coefficient['coefficient_cession']

        data_expenses = []
        total_summa_exp = 0
        for category in expenses_category:
            expenses_cat_id: int = category.id
            expenses_name = category.name

            if date_1:
                expenses_query = await session.execute(select(expenses).where(and_(or_(expenses.c.cession_id.is_(None),
                                                                                       expenses.c.cession_id == cession_id),
                                                                                   expenses.c.expenses_category_id == expenses_cat_id,
                                                                                   expenses.c.date >= date_1, expenses.c.date <= date_2)))
            else:
                expenses_query = await session.execute(select(expenses).where(and_(or_(expenses.c.cession_id.is_(None),
                                                                                       expenses.c.cession_id == cession_id),
                                                                                   expenses.c.expenses_category_id == expenses_cat_id)))

            summa_exp_category = 0
            for item_exp in expenses_query.mappings().all():

                if item_exp.cession_id and item_exp.cession_id == cession_id:

                    summa_exp = item_exp.summa / 100
                    summa_exp_category += summa_exp

                else:
                    summa_exp = item_exp.summa / 100 * coefficient_cession
                    summa_exp_category += summa_exp

            total_summa_exp += summa_exp_category

            data_expenses.append({'expenses_name': expenses_name,
                                  'summa_exp_category': round(summa_exp_category, 2)})

        cession_expenses.append({
            "cession_id": cession_id,
            "cession_name": cession_name,
            "data_expenses": data_expenses,
            "total_summa_exp": total_summa_exp
        })

    return cession_expenses


'''
Функция расчета Чистой прибыли по cession_id
'''


async def get_profit_cession(data,  session):

    revenue_cession = await get_revenue(data,  session)

    profit = []
    for item in revenue_cession:
        summa_revenue = item['summa_revenue']
        cession_id = item['cession_id']

        data_expenses = {
            "cession_id": cession_id,
            "date_1": data['date_1'],
            "date_2": data['date_2'],
        }

        expenses_cession = await get_expenses_cession(data_expenses,  session)
        summa_expenses = expenses_cession[0]['total_summa_exp']

        profit_cession = round(summa_revenue - summa_expenses, 2)

        profit.append({
            "cession_id": cession_id,
            "cession_name": item['cession_name'],
            "profit_cession": profit_cession,
        })

    return profit


'''
Основная функция Статистика в разрезе Портфелей(Цессий)
'''


async def get_statistic(data,  session):

    dates = data['dates']
    date_format_1 = ''
    date_format_2 = ''
    cession_array = data['cession_array']
    payment_total = 0
    expenses_total = 0
    accrual_expenses_total = 0

    payment_total_query = None
    expenses_total_query = None
    accrual_total_query = None

    if len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1
    elif len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    if date_1:
        date_format_1 = datetime.strptime(str(date_1), '%Y-%m-%d').strftime("%d.%m.%Y")
        date_format_2 = datetime.strptime(str(date_2), '%Y-%m-%d').strftime("%d.%m.%Y")

    if len(cession_array) > 0:
        for cession_item in cession_array:
            cession_id: int = cession_item['id']

            credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
            credits_id_list = credits_id_query.scalars().all()

            if date_1:
                payment_total_query = await session.execute(select(func.sum(payment.c.summa)).
                                                            filter(and_(payment.c.date >= date_1, payment.c.date <= date_2, payment.c.credit_id.in_(credits_id_list))))
                expenses_total_query = await session.execute(select(func.sum(expenses.c.summa)).
                                                             filter(and_(expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                         expenses.c.cession_id == cession_id)))
                accrual_total_query = await session.execute(select(func.sum(expenses.c.summa)).
                                                            filter(and_(expenses.c.date.is_(None),
                                                                        expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                        expenses.c.cession_id == cession_id)))
            else:
                payment_total_query = await session.execute(select(func.sum(payment.c.summa)).filter(payment.c.credit_id.in_(credits_id_list)))
                expenses_total_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.date.isnot(None))))
                accrual_total_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.date.is_(None))))

        cessions_list_for_statistic = cession_array
    else:
        if date_1:
            payment_total_query = await session.execute(select(func.sum(payment.c.summa)).
                                                        filter(and_(payment.c.date >= date_1, payment.c.date <= date_2)))
            expenses_total_query = await session.execute(select(func.sum(expenses.c.summa)).
                                                         filter(and_(expenses.c.date >= date_1, expenses.c.date <= date_2)))
            accrual_total_query = await session.execute(select(func.sum(expenses.c.summa)).
                                                        filter(and_(expenses.c.date.is_(None),
                                                                    expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2)))
        else:
            payment_total_query = await session.execute(select(func.sum(payment.c.summa)))
            expenses_total_query = await session.execute(select(func.sum(expenses.c.summa)).filter(expenses.c.date.isnot(None)))
            accrual_total_query = await session.execute(select(func.sum(expenses.c.summa)).filter(expenses.c.date.is_(None)))

        cession_query = await session.execute(select(cession))
        cessions_list_for_statistic = cession_query.mappings().all()

    payment_total_ans = payment_total_query.scalar()
    expenses_total_ans = expenses_total_query.scalar()
    accrual_total_ans = accrual_total_query.scalar()

    if payment_total_ans:
        payment_total = payment_total_ans / 100

    if expenses_total_ans:
        expenses_total = expenses_total_ans / 100

    if accrual_total_ans:
        accrual_expenses_total = accrual_total_ans / 100

    profit_total = round(payment_total - expenses_total - accrual_expenses_total, 2)

    data_statistic = []
    for item in cessions_list_for_statistic:

        summa_pay_cess = 0
        summa_expenses_cess = 0
        summa_accrual_cess = 0

        cession_id: int = item.id
        cession_name = item.name

        data_coefficient = await get_coefficient_cession(cession_id,  session)
        coefficient_cession = data_coefficient['coefficient_cession']
        cession_number_credit = data_coefficient['cession_number_credit_active']
        cession_number_credit_total = data_coefficient['cession_number_credit_total']

        credits_id_query = await session.execute(select(credit.c.id).where(credit.c.cession_id == cession_id))
        credits_id_list = credits_id_query.scalars().all()

        if len(credits_id_list) > 0:
            if date_1:
                summa_pay_query = await session.execute(select(func.sum(payment.c.summa)).filter(and_(payment.c.date >= date_1,
                                                                                                      payment.c.date <= date_2,
                                                                                                      payment.c.credit_id.in_(credits_id_list))))
                summa_expenses_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date >= date_1,
                                                                                                            expenses.c.date <= date_2,
                                                                                                            expenses.c.cession_id == cession_id)))
                summa_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date_accrual >= date_1,
                                                                                                           expenses.c.date_accrual <= date_2,
                                                                                                           expenses.c.cession_id == cession_id,
                                                                                                           expenses.c.date.is_(None))))
            else:
                summa_pay_query = await session.execute(select(func.sum(payment.c.summa)).filter(payment.c.credit_id.in_(credits_id_list)))
                summa_expenses_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.date.isnot(None))))
                summa_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.cession_id == cession_id, expenses.c.date.is_(None))))

            summa_pay = summa_pay_query.scalar()
            summa_expenses = summa_expenses_query.scalar()
            summa_accrual = summa_accrual_query.scalar()

            if summa_pay:
                summa_pay_cess = round(summa_pay / 100, 2)

            if summa_expenses:
                summa_expenses_cess = round(summa_expenses / 100, 2)

            if summa_accrual:
                summa_accrual_cess = round(summa_accrual / 100, 2)

            data_statistic.append({
                "cession_id": cession_id,
                "cession_name": cession_name,
                "coefficient_cession": round(coefficient_cession * 100, 2),
                "cession_number_credit_total": cession_number_credit_total,
                "cession_number_credit": cession_number_credit,
                "summa_pay_cess": summa_pay_cess,
                "summa_expenses_cess": summa_expenses_cess,
                "summa_accrual_cess": summa_accrual_cess,
            })

    expenses_category_query = await session.execute(select(ref_expenses_category))

    data_expenses_category = []
    data_accrual_expenses_category = []
    data_total_accrual_category = []
    for item_cat in expenses_category_query.mappings().all():
        category_id: int = item_cat.id
        category = item_cat.name

        if len(cession_array) > 0:

            cession_id_list = []
            for cession_item in cession_array:
                cession_id_list.append(cession_item['id'])

            if date_1:
                category_summa_expenses_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                                                     expenses.c.cession_id.in_(cession_id_list),
                                                                                                                     expenses.c.expenses_category_id == category_id)))
                category_summa_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date.is_(None),
                                                                                                                    expenses.c.cession_id.in_(cession_id_list),
                                                                                                                    expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                                                    expenses.c.expenses_category_id == category_id)))
                category_total_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date.is_(None),
                                                                                                                    expenses.c.cession_id.in_(cession_id_list),
                                                                                                                    expenses.c.date_accrual <= date_2,
                                                                                                                    expenses.c.expenses_category_id == category_id)))
            else:
                category_summa_expenses_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == category_id,
                                                                                                                     expenses.c.cession_id.in_(cession_id_list),
                                                                                                                     expenses.c.date.isnot(None))))
                category_summa_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == category_id,
                                                                                                                    expenses.c.cession_id.in_(cession_id_list),
                                                                                                                    expenses.c.date.is_(None))))
                category_total_accrual_query = category_summa_accrual_query

            category_summa_expenses = category_summa_expenses_query.scalar()
            category_summa_accrual = category_summa_accrual_query.scalar()
            category_total_accrual = category_total_accrual_query.scalar()

            if category_summa_expenses:
                category_summa = round(category_summa_expenses / 100, 2)
                data_expenses_category.append({
                    "category_id": category_id,
                    "category": category,
                    "category_summa": category_summa,
                })

            if category_summa_accrual:
                category_accrual_summa = round(category_summa_accrual / 100, 2)
                data_accrual_expenses_category.append({
                    "category_id": category_id,
                    "category": category,
                    "category_accrual_summa": category_accrual_summa,
                })

            if category_total_accrual:
                category_total_accrual_summa = round(category_total_accrual / 100, 2)
                data_total_accrual_category.append({
                    "category_id": category_id,
                    "category": category,
                    "category_total_accrual_summa": category_total_accrual_summa,
                })

        else:
            if date_1:
                category_summa_expenses_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date >= date_1, expenses.c.date <= date_2,
                                                                                                                     expenses.c.expenses_category_id == category_id)))
                category_summa_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date.is_(None),
                                                                                                                    expenses.c.date_accrual >= date_1, expenses.c.date_accrual <= date_2,
                                                                                                                     expenses.c.expenses_category_id == category_id)))
                category_total_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.date.is_(None),
                                                                                                                    expenses.c.date_accrual <= date_2,
                                                                                                                    expenses.c.expenses_category_id == category_id)))
            else:
                category_summa_expenses_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == category_id, expenses.c.date.isnot(None))))
                category_summa_accrual_query = await session.execute(select(func.sum(expenses.c.summa)).filter(and_(expenses.c.expenses_category_id == category_id, expenses.c.date.is_(None))))
                category_total_accrual_query = category_summa_accrual_query

            category_summa_expenses = category_summa_expenses_query.scalar()
            category_summa_accrual = category_summa_accrual_query.scalar()
            category_total_accrual = category_total_accrual_query.scalar()

            if category_summa_expenses:
                category_summa = round(category_summa_expenses / 100, 2)
                data_expenses_category.append({
                    "category_id": category_id,
                    "category": category,
                    "category_summa": category_summa,
                })

            if category_summa_accrual:
                category_accrual_summa = round(category_summa_accrual / 100, 2)
                data_accrual_expenses_category.append({
                    "category_id": category_id,
                    "category": category,
                    "category_accrual_summa": category_accrual_summa,
                })

            if category_total_accrual:
                category_total_accrual_summa = round(category_total_accrual / 100, 2)
                data_total_accrual_category.append({
                    "category_id": category_id,
                    "category": category,
                    "category_total_accrual_summa": category_total_accrual_summa,
                })

    return {
        'date_1': date_format_1,
        'date_2': date_format_2,
        'payment_total': payment_total,
        'expenses_total': expenses_total,
        'accrual_expenses_total': accrual_expenses_total,
        'profit_total': profit_total,
        'data_statistic': data_statistic,
        'data_expenses_category': data_expenses_category,
        'data_accrual_expenses_category': data_accrual_expenses_category,
        'data_total_accrual_category': data_total_accrual_category
    }