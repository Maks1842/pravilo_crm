from datetime import date, datetime

from sqlalchemy import select, insert, func, distinct, update, desc, and_

from src.collection_debt.models import *


async def get_collection_debt_all(per_page: int, data, session):

    page = data['page']
    credit_id: int = data['credit_id']
    type_department_id: int = data['type_department_id']
    department_id: int = data['department_id']
    dates = data['dates']

    if len(dates) == 1:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = date_1
    elif len(dates) == 2:
        date_1 = datetime.strptime(dates[0], '%Y-%m-%d').date()
        date_2 = datetime.strptime(dates[1], '%Y-%m-%d').date()
    else:
        date_1 = None
        date_2 = None

    if credit_id:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.credit_id == credit_id).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.credit_id == credit_id))
    elif credit_id is None and date_1 and department_id is None and type_department_id is None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= date_1, collection_debt.c.date_start <= date_2)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= date_1, collection_debt.c.date_start <= date_2)))
    elif credit_id is None and date_1 is None and department_id is None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.type_department_id == type_department_id).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.type_department_id == type_department_id))
    elif credit_id is None and date_1 and department_id is None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    elif credit_id is None and date_1 is None and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    elif credit_id is None and date_1 and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    else:
        collect_query = await session.execute(select(collection_debt).order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set


async def get_mov_all(per_page: int, data, session):

    page = data['page']
    filter_components = data['filter_components']
    list_cession = filter_components['cession_id_list']
    list_type_dep = filter_components['type_dep_id_list']
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

    if len(list_cession) == 0 and len(list_type_dep) == 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2)))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.credit_id.in_(credits_id_list)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.credit_id.in_(credits_id_list)))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2)))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1 is None:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.type_department_id.in_(list_type_dep)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.type_department_id.in_(list_type_dep)))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2)))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep))))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2)))
    else:
        collect_query = await session.execute(select(collection_debt).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set


async def get_mov_datenone_ret_end(per_page: int, data, session):
    page = data['page']
    filter_components = data['filter_components']
    list_cession = filter_components['cession_id_list']
    list_type_dep = filter_components['type_dep_id_list']
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

    if len(list_cession) == 0 and len(list_type_dep) == 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1 is None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    else:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_return.is_(None), collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_return.is_(None), collection_debt.c.date_end.is_(None))))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set


async def get_mov_date_ret_endnone(per_page: int, data, session):
    page = data['page']
    filter_components = data['filter_components']
    list_cession = filter_components['cession_id_list']
    list_type_dep = filter_components['type_dep_id_list']
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

    if len(list_cession) == 0 and len(list_type_dep) == 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1 is None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    else:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_return.isnot(None), collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_return.isnot(None), collection_debt.c.date_end.is_(None))))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set


async def get_mov_date_end(per_page: int, data, session):
    page = data['page']
    filter_components = data['filter_components']
    list_cession = filter_components['cession_id_list']
    list_type_dep = filter_components['type_dep_id_list']
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

    if len(list_cession) == 0 and len(list_type_dep) == 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif len(list_cession) > 0 and len(list_type_dep) == 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1 is None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif len(list_cession) == 0 and len(list_type_dep) > 0 and date_1:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1 is None:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif len(list_cession) > 0 and len(list_type_dep) > 0 and date_1:
        credit_query = await session.execute(select(credit.c.id).where(credit.c.cession_id.in_(list_cession)))
        credits_id_list = credit_query.scalars().all()

        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                 collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                 collection_debt.c.date_start >= date_1,
                                                                                 collection_debt.c.date_start <= date_2,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id.in_(credits_id_list),
                                                                                                                   collection_debt.c.type_department_id.in_(list_type_dep),
                                                                                                                   collection_debt.c.date_start >= date_1,
                                                                                                                   collection_debt.c.date_start <= date_2,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    else:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.date_end.isnot(None)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.date_end.isnot(None)))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set