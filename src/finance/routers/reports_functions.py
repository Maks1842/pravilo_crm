from sqlalchemy import select, insert, func, distinct, update, and_, desc
from src.debts.models import cession, credit
from src.payments.models import payment

from datetime import datetime, timedelta


async def get_revenue(data_json,  session):

    data = data_json['data_json']

    dates_1 = data['dates_1']
    dates_2 = data['dates_2']
    cession_id_list = data['cession_id_list']

    if dates_2 is None:
        dates_2 = dates_1

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
        print(credits_id_list)

        if len(credits_id_list) > 0:
            if dates_1 == None:
                summa_query = await session.execute(select(func.sum(payment.c.summa)).filter(payment.c.credit_id.in_(credits_id_list)))
            else:
                summa_query = await session.execute(select(func.sum(payment.c.summa)).
                                                    filter(and_(payment.c.date >= dates_1, payment.c.date <= dates_2, payment.c.credit_id.in_(credits_id_list))))

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

            print(data_revenue)


    return data_revenue