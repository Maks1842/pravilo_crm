from datetime import date, datetime

from sqlalchemy import select, insert, func, distinct, update, desc, and_

from src.collection_debt.models import *


async def get_collection_debt_all(per_page: int, data, session):

    page = data['page']
    credit_id: int = data['credit_id']
    type_department_id: int = data['type_department_id']
    department_id: int = data['department_id']
    dates1 = data['dates1']
    dates2 = data['dates2']

    if dates2 == None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    if credit_id:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.credit_id == credit_id).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.credit_id == credit_id))
    elif credit_id == None and dates1 and department_id == None and type_department_id == None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2)))
    elif credit_id == None and dates1 == None and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.type_department_id == type_department_id).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.type_department_id == type_department_id))
    elif credit_id == None and dates1 and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    elif credit_id == None and dates1 == None and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    elif credit_id == None and dates1 and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    else:
        collect_query = await session.execute(select(collection_debt).order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set


async def get_collection_debt_1(data, session):
    page = data['page']
    per_page = data['per_page']
    credit_id: int = data['credit_id']
    type_department_id: int = data['type_department_id']
    department_id: int = data['department_id']
    dates1 = data['dates1']
    dates2 = data['dates2']

    if dates2 == None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    if credit_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id == credit_id,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id == credit_id,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 and department_id == None and type_department_id == None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.date_return.is_(None), collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 == None and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 == None and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id),
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None)))
    elif credit_id == None and dates1 and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.is_(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.is_(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    else:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_return.is_(None), collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_return.is_(None), collection_debt.c.date_end.is_(None))))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set


async def get_collection_debt_2(data, session):
    page = data['page']
    per_page = data['per_page']
    credit_id: int = data['credit_id']
    type_department_id: int = data['type_department_id']
    department_id: int = data['department_id']
    dates1 = data['dates1']
    dates2 = data['dates2']

    if dates2 == None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    if credit_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id == credit_id,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id == credit_id,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 and department_id == None and type_department_id == None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.date_return.isnot(None), collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 == None and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    elif credit_id == None and dates1 == None and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id),
                                                                                                              collection_debt.c.date_return.isnot(None),
                                                                                                              collection_debt.c.date_end.is_(None)))
    elif credit_id == None and dates1 and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.isnot(None),
                                                                                 collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.isnot(None),
                                                                                                                   collection_debt.c.date_end.is_(None))))
    else:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_return.isnot(None), collection_debt.c.date_end.is_(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_return.isnot(None), collection_debt.c.date_end.is_(None))))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set


async def get_collection_debt_3(data, session):
    page = data['page']
    per_page = data['per_page']
    credit_id: int = data['credit_id']
    type_department_id: int = data['type_department_id']
    department_id: int = data['department_id']
    dates1 = data['dates1']
    dates2 = data['dates2']

    if dates2 == None:
        dates2 = dates1

    if dates1 is not None:
        dates1 = datetime.strptime(dates1, '%Y-%m-%d').date()
        dates2 = datetime.strptime(dates2, '%Y-%m-%d').date()

    if credit_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.credit_id == credit_id,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.credit_id == credit_id,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif credit_id == None and dates1 and department_id == None and type_department_id == None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif credit_id == None and dates1 == None and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif credit_id == None and dates1 and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    elif credit_id == None and dates1 == None and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id),
                                                                                                              collection_debt.c.date_end.isnot(None)))
    elif credit_id == None and dates1 and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_end.isnot(None))).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_end.isnot(None))))
    else:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.date_end.isnot(None)).
                                              order_by(desc(collection_debt.c.date_start), desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.date_end.isnot(None)))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set