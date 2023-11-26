from sqlalchemy import select, insert, func, distinct, update, and_, or_
from src.debts.models import cession, credit
from src.payments.models import payment
from src.finance.models import expenses, ref_expenses_category

from datetime import datetime, timedelta


'''
Функция получения суммы выручки(платежей) в разрезе Портфелей(Цессий)
'''
async def get_revenue(data,  session):

    date_1 = data['date_1']
    date_2 = data['date_2']
    cession_id = data['cession_id']

    if date_2 is None:
        date_2 = date_1

    if date_1 is not None:
        date_1 = datetime.strptime(date_1, '%Y-%m-%d').date()
        date_2 = datetime.strptime(date_2, '%Y-%m-%d').date()

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
        else:
            if date_1 == None:
                summa_query = await session.execute(select(func.sum(payment.c.summa)))
            else:
                summa_query = await session.execute(select(func.sum(payment.c.summa)).
                                                    filter(and_(payment.c.date >= date_1, payment.c.date <= date_2)))

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

    total_credit_query = await session.execute(select(func.count(distinct(credit.c.id)).filter(credit.c.parent_id.is_(None))))
    total_credit = total_credit_query.scalar()

    # cession_query = await session.execute(select(cession))
    #
    # coefficient_data = []
    # for item in cession_query.mappings().all():
    #     cession_id: int = item.id
    cession_number_credit_query = await session.execute(select(func.count(distinct(credit.c.id)).filter(and_(credit.c.cession_id == cession_id), credit.c.parent_id.is_(None))))
    cession_number_credit = cession_number_credit_query.scalar()

    coefficient_cession = round(cession_number_credit / total_credit, 2)

    # coefficient_data = {
    #     'cession_id': cession_id,
    #     'cession_name': item.name,
    #     'coefficient_cession': coefficient_cession,
    # }

    return coefficient_cession


'''
Функция получения суммы расходов в разрезе Портфелей(Цессий).
Расходы с идентификатором cession_id покрываются за счет доходов данного портфеля,
если нет идентификатора cession_id, то расходы рассчитываются пропорционально долям Портфелей.
Результат выводится в разрезе категорий расходов.
'''
async def get_expenses_cession(data,  session):

    date_1 = data['date_1']
    date_2 = data['date_2']
    cession_id = data['cession_id']

    if date_2 is None:
        date_2 = date_1

    if date_1:
        date_1 = datetime.strptime(date_1, '%Y-%m-%d').date()
        date_2 = datetime.strptime(date_2, '%Y-%m-%d').date()

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

        coefficient_cession = await get_coefficient_cession(cession_id,  session)

        data_expenses = []
        for category in expenses_category:
            expenses_cat_id: int = category.id
            expenses_name = category.name

            if date_1:
                expenses_query = await session.execute(select(expenses).where(and_(or_(expenses.c.cession_id.is_(None), expenses.c.cession_id == cession_id), expenses.c.expenses_category_id == expenses_cat_id, expenses.c.date >= date_1, expenses.c.date <= date_2)))
            else:
                expenses_query = await session.execute(select(expenses).where(and_(or_(expenses.c.cession_id.is_(None), expenses.c.cession_id == cession_id), expenses.c.expenses_category_id == expenses_cat_id)))

            summa_exp_category = 0
            for item_exp in expenses_query.mappings().all():

                if item_exp.cession_id and item_exp.cession_id == cession_id:

                    summa_exp = item_exp.summa / 100
                    summa_exp_category += summa_exp

                else:
                    summa_exp = item_exp.summa / 100 * coefficient_cession
                    summa_exp_category += summa_exp

            data_expenses.append({'expenses_name': expenses_name,
                                  'summa_exp_category': round(summa_exp_category, 2)})

        cession_expenses.append({
            "cession_id": cession_id,
            "cession_name": cession_name,
            "data_expenses": data_expenses,
        })

    return cession_expenses