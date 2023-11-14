from sqlalchemy import select, insert, func, distinct, update, and_, desc
from src.debts.models import cession, credit
from src.payments.models import payment

from datetime import datetime, timedelta


'''
Функция получения суммы выручки(платежей) в разрезе Портфелей(Цессий)
'''
async def get_revenue(data,  session):

    date_1 = data['date_1']
    date_2 = data['date_2']
    cession_id_list = data['cession_id_list']

    if date_2 is None:
        date_2 = date_1

    if date_1 is not None:
        date_1 = datetime.strptime(date_1, '%Y-%m-%d').date()
        date_2 = datetime.strptime(date_2, '%Y-%m-%d').date()

    if len(cession_id_list) > 0:
        cession_query = await session.execute(select(cession).where(cession.c.id.in_(cession_id_list)))

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
Функция расчета коэффициентов(долей) каждого Портфеля в общей структуре
Вес рассчитывается по количеству КД в портфеле
Учитываются только базовые(родительские) КД, производные(дочерние) в расчет не берутся
'''
async def get_coefficient_cession(data,  session):

    total_credit_query = await session.execute(select(func.count(distinct(credit.c.id)).filter(credit.c.parent_id == None)))
    total_credit = total_credit_query.scalar()

    cession_query = await session.execute(select(cession))

    coefficient_data = []
    for item in cession_query.mappings().all():
        cession_id: int = item.id
        cession_number_credit_query = await session.execute(select(func.count(distinct(credit.c.id)).filter(and_(credit.c.cession_id == cession_id), credit.c.parent_id == None)))
        cession_number_credit = cession_number_credit_query.scalar()

        coefficient_cession = round(cession_number_credit / total_credit, 2)

        coefficient_data.append({
            'cession_id': cession_id,
            'cession_name': item.name,
            'coefficient_cession': coefficient_cession,
        })



    return coefficient_data