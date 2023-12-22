from datetime import date, datetime

from sqlalchemy import select, insert, func, distinct, update, desc, and_

from src.collection_debt.models import *


async def get_execut_prod_all(per_page: int, data, session):

    page: int = data['page']
    credit_id: int = data['credit_id']
    debtor_id: int = data['debtor_id']
    ep_id: int = data['ep_id']

    if ep_id:
        query = await session.execute(select(executive_productions).where(executive_productions.c.id == ep_id).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))
        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(executive_productions.c.id == ep_id))
    elif credit_id and ep_id is None:
        query = await session.execute(select(executive_productions).where(executive_productions.c.credit_id == credit_id).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))
        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(executive_productions.c.credit_id == credit_id))
    elif credit_id is None and debtor_id and ep_id is None:
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
    list_type_ed = filter_components['type_ed_id_list']
    dates = filter_components['dates']

    if len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1
    elif len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    if len(list_cession) == 0 and len(list_type_ed) == 0 and date_1:
        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.date_end.is_(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.date_end.is_(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    elif len(list_cession) > 0 and len(list_type_ed) == 0 and date_1 is None:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.date_end.is_(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_ed) == 0 and date_1:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.date_end.is_(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.date_end.is_(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    elif len(list_cession) == 0 and len(list_type_ed) > 0 and date_1 is None:
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.is_(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.is_(None))))
    elif len(list_cession) == 0 and len(list_type_ed) > 0 and date_1:
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.is_(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.is_(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    elif len(list_cession) > 0 and len(list_type_ed) > 0 and date_1 is None:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.is_(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_ed) > 0 and date_1:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.is_(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.is_(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    else:
        query = await session.execute(select(executive_productions).where(executive_productions.c.date_end.is_(None)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(executive_productions.c.date_end.is_(None)))

    ep_set = {'ep_query': query, 'total_ep_query': total_ep_query}

    return ep_set


async def get_ep_date_end(per_page: int, data, session):

    page = data['page']
    filter_components = data['filter_components']
    list_cession = filter_components['cession_id_list']
    list_type_ed = filter_components['type_ed_id_list']
    dates = filter_components['dates']

    if len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1
    elif len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    if len(list_cession) == 0 and len(list_type_ed) == 0 and date_1:
        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.date_end.isnot(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.date_end.isnot(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    elif len(list_cession) > 0 and len(list_type_ed) == 0 and date_1 is None:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.date_end.isnot(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.date_end.isnot(None))))
    elif len(list_cession) > 0 and len(list_type_ed) == 0 and date_1:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.date_end.isnot(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.date_end.isnot(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    elif len(list_cession) == 0 and len(list_type_ed) > 0 and date_1 is None:
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.isnot(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.isnot(None))))
    elif len(list_cession) == 0 and len(list_type_ed) > 0 and date_1:
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.isnot(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.isnot(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    elif len(list_cession) > 0 and len(list_type_ed) > 0 and date_1 is None:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.isnot(None))).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.isnot(None))))
    elif len(list_cession) > 0 and len(list_type_ed) > 0 and date_1:
        credit_cession_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        list_credit = credit_cession_query.scalars().all()
        list_ed_query = await session.execute(select(executive_document.c.id).where(executive_document.c.type_ed_id.in_(list_type_ed)))
        list_ed_id = list_ed_query.scalars().all()

        query = await session.execute(select(executive_productions).where(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                               executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                               executive_productions.c.date_end.isnot(None),
                                                                               executive_productions.c.date_on >= date_1,
                                                                               executive_productions.c.date_on <= date_2)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(and_(executive_productions.c.credit_id.in_(list_credit),
                                                                                                                    executive_productions.c.executive_document_id.in_(list_ed_id),
                                                                                                                    executive_productions.c.date_end.isnot(None),
                                                                                                                    executive_productions.c.date_on >= date_1,
                                                                                                                    executive_productions.c.date_on <= date_2)))
    else:
        query = await session.execute(select(executive_productions).where(executive_productions.c.date_end.isnot(None)).
                                      order_by(desc(executive_productions.c.date_on)).limit(per_page).offset((page - 1) * per_page))

        total_ep_query = await session.execute(select(func.count(distinct(executive_productions.c.id))).filter(executive_productions.c.date_end.isnot(None)))

    ep_set = {'ep_query': query, 'total_ep_query': total_ep_query}

    return ep_set
