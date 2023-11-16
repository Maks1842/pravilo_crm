import math
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.collection_debt.models import *
from src.references.models import ref_rosp, ref_bank, ref_pfr, ref_type_department


async def get_collection_debt_all(data, session):

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
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.credit_id == credit_id).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.credit_id == credit_id))
    elif credit_id == None and dates1 and department_id == None and type_department_id == None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2)).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2)))
    elif credit_id == None and dates1 == None and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.type_department_id == type_department_id).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.type_department_id == type_department_id))
    elif credit_id == None and dates1 and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    elif credit_id == None and dates1 == None and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    elif credit_id == None and dates1 and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id)).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id)))
    else:
        collect_query = await session.execute(select(collection_debt).order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
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
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.credit_id == credit_id).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.credit_id == credit_id))
    elif credit_id == None and dates1 and department_id == None and type_department_id == None:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2, collection_debt.c.date_return.is_(None))).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1, collection_debt.c.date_start <= dates2, collection_debt.c.date_return.is_(None))))
    elif credit_id == None and dates1 == None and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.type_department_id == type_department_id, collection_debt.c.date_return.is_(None))).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.type_department_id == type_department_id, collection_debt.c.date_return.is_(None))))
    elif credit_id == None and dates1 and department_id == None and type_department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.is_(None))).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.is_(None))))
    elif credit_id == None and dates1 == None and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.is_(None))).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id),
                                                                                                                   collection_debt.c.date_return.is_(None)))
    elif credit_id == None and dates1 and department_id:
        collect_query = await session.execute(select(collection_debt).where(and_(collection_debt.c.date_start >= dates1,
                                                                                 collection_debt.c.date_start <= dates2,
                                                                                 collection_debt.c.department_presentation_id == department_id,
                                                                                 collection_debt.c.type_department_id == type_department_id,
                                                                                 collection_debt.c.date_return.is_(None))).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(and_(collection_debt.c.date_start >= dates1,
                                                                                                                   collection_debt.c.date_start <= dates2,
                                                                                                                   collection_debt.c.department_presentation_id == department_id,
                                                                                                                   collection_debt.c.type_department_id == type_department_id,
                                                                                                                   collection_debt.c.date_return.is_(None))))
    else:
        collect_query = await session.execute(select(collection_debt).where(collection_debt.c.date_return.is_(None)).
                                              order_by(desc(collection_debt.c.date_start)).order_by(desc(collection_debt.c.id)).
                                              limit(per_page).offset((page - 1) * per_page))
        total_collect_query = await session.execute(select(func.count(distinct(collection_debt.c.id))).filter(collection_debt.c.date_return.is_(None)))

    coll_deb_set = {'collect_query': collect_query, 'total_collect_query': total_collect_query}

    return coll_deb_set
#
#
# def get_collection_debt_2(data):
#
#     credit_id = data['credit_id']
#     type_department_id = data['type_department_id']
#     department_id = data['department_id']
#     dates1 = data['dates1']
#     dates2 = data['dates2']
#
#     if dates2 == None:
#         dates2 = dates1
#
#     if credit_id == None and dates1 and department_id == None and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(date_start__range=[dates1, dates2], date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#     elif credit_id and dates1 == None and department_id == None and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(credit_id=credit_id, date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#     elif credit_id and dates1 and department_id == None and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(credit_id=credit_id, date_start__range=[dates1, dates2], date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#     elif dates1 == None and department_id and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(department_presentation_id=department_id, date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#     elif dates1 and department_id and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(date_start__range=[dates1, dates2], department_presentation_id=department_id, date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#     elif dates1 == None and type_department_id:
#         coll_deb_set = Collection_Debt.objects.filter(type_department_id=type_department_id, date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#     elif dates1 and type_department_id:
#         coll_deb_set = Collection_Debt.objects.filter(date_start__range=[dates1, dates2], type_department_id=type_department_id, date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#     else:
#         coll_deb_set = Collection_Debt.objects.filter(date_return__isnull=False, date_end__isnull=True).values().order_by('-date_start', '-pk')
#
#     return coll_deb_set
#
#
# def get_collection_debt_3(data):
#
#     credit_id = data['credit_id']
#     type_department_id = data['type_department_id']
#     department_id = data['department_id']
#     dates1 = data['dates1']
#     dates2 = data['dates2']
#
#     if dates2 == None:
#         dates2 = dates1
#
#     if credit_id == None and dates1 and department_id == None and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(date_start__range=[dates1, dates2], date_end__isnull=False).values().order_by('-date_start', '-pk')
#     elif credit_id and dates1 == None and department_id == None and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(credit_id=credit_id, date_end__isnull=False).values().order_by('-date_start', '-pk')
#     elif credit_id and dates1 and department_id == None and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(credit_id=credit_id, date_start__range=[dates1, dates2], date_end__isnull=False).values().order_by('-date_start', '-pk')
#     elif dates1 == None and department_id and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(department_presentation_id=department_id, date_end__isnull=False).values().order_by('-date_start', '-pk')
#     elif dates1 and department_id and type_department_id == None:
#         coll_deb_set = Collection_Debt.objects.filter(date_start__range=[dates1, dates2], department_presentation_id=department_id, date_end__isnull=False).values().order_by('-date_start', '-pk')
#     elif dates1 == None and type_department_id:
#         coll_deb_set = Collection_Debt.objects.filter(type_department_id=type_department_id, date_end__isnull=False).values().order_by('-date_start', '-pk')
#     elif dates1 and type_department_id:
#         coll_deb_set = Collection_Debt.objects.filter(date_start__range=[dates1, dates2], type_department_id=type_department_id, date_end__isnull=False).values().order_by('-date_start', '-pk')
#     else:
#         coll_deb_set = Collection_Debt.objects.filter(date_end__isnull=False).values().order_by('-date_start', '-pk')
#
#     return coll_deb_set