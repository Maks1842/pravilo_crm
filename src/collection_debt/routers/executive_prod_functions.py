from datetime import date, datetime

from sqlalchemy import select, insert, func, distinct, update, desc, and_

from src.collection_debt.models import *


async def get_execut_prod_all(per_page: int, data, session):

    page: int = data['page']
    credit_id: int = data['credit_id']
    debtor_id: int = data['debtor_id']

    if credit_id:
        query = await session.execute(select(executive_productions).where(executive_productions.c.credit_id == credit_id).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))
        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(executive_productions.c.credit_id == credit_id))
    elif credit_id is None and debtor_id:
        query_credit_id = await session.execute(select(credit.c.id).where(credit.c.debtor_id == debtor_id))
        credits_id_list = query_credit_id.scalars().all()

        query = await session.execute(select(executive_productions).where(executive_productions.c.credit_id.in_(credits_id_list)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))
        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(executive_productions.c.credit_id.in_(credits_id_list)))
    else:
        query = await session.execute(select(executive_productions).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))))

    ep_set = {'ep_query': query, 'total_ep_query': total_ep_query}

    return ep_set


async def get_ep_date_on(per_page: int, data, session):

    page = data['page']
    filter_components = data['filter_components']
    list_cession = filter_components['cession_id_list']

    if len(list_cession) == 0:
        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.date_on.isnot(None), executive_productions.c.date_end.is_(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.date_on.isnot(None), executive_productions.c.date_end.is_(None))))
    else:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit), executive_productions.c.date_on.isnot(None), executive_productions.c.date_end.is_(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit), executive_productions.c.date_on.isnot(None), executive_productions.c.date_end.is_(None))))

    ep_set = {'ep_query': query, 'total_ep_query': total_ep_query}

    return ep_set


async def get_ep_date_end(per_page: int, data, session):

    page = data['page']
    filter_components = data['filter_components']
    list_cession = filter_components['cession_id_list']

    if len(list_cession) == 0:
        query = await session.execute(select(executive_productions).where(executive_productions.c.date_end.isnot(None)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(executive_productions.c.date_end.isnot(None)))
    else:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit), executive_productions.c.date_end.isnot(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit), executive_productions.c.date_end.isnot(None))))

    ep_set = {'ep_query': query, 'total_ep_query': total_ep_query}

    return ep_set
