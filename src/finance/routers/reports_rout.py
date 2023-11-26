from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, func, distinct, update, and_, desc

from src.database import get_async_session
from src.finance.routers.reports_functions import get_revenue, get_expenses_cession
from src.debts.models import cession


# Получить отчеты по головной организации
router_report_parent_organisation = APIRouter(
    prefix="/v1/ReportParentOrganisation",
    tags=["Finance"]
)


@router_report_parent_organisation.post("/")
async def report_parent_organisation(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    # test_result = await get_coefficient_cession(data_json, session)
    # return test_result



    profit_check = data_json['profit_check']
    statistic_check = data_json['statistic_check']

    if 'date_1' not in data_json:
        data_json["date_1"] = None
    if 'date_2' not in data_json:
        data_json["date_2"] = None

    data_json["cession_id_list"] = []

    if profit_check:
        try:
            result = await get_revenue(data_json, session)

            return result

            # return {
            #     'status': 'success',
            #     'data': None,
            #     'details': f'Успешною {result}'
            # }
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": ex
            }
    elif statistic_check:
        try:
            result = await get_expenses_cession(data_json, session)

            return result
            # return {
            #     'status': 'success',
            #     'data': None,
            #     'details': f'Успешною {result}'
            # }
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": ex
            }




# Получить отчеты для Инвестора
router_report_for_investor = APIRouter(
    prefix="/v1/ReportForInvestor",
    tags=["Finance"]
)


@router_report_for_investor.post("/")
async def report_for_investor(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    profit_check = data_json['profit_check']
    statistic_check = data_json['statistic_check']
    lending_id: int = data_json['lending_id']

    cession_id_query = await session.execute(select(cession.c.id).where(cession.c.lending_id == lending_id))
    data_json["cession_id_list"] = cession_id_query.scalars().all()


    if 'date_1' not in data_json:
        data_json["date_1"] = None
    if 'date_2' not in data_json:
        data_json["date_2"] = None

    if profit_check:

        try:
            result = await get_revenue(data_json, session)

            return {
                'status': 'success',
                'data': None,
                'details': f'Успешною {result}'
            }
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": ex
            }


# data_json: {
#     "dates_1": None,
#     "dates_2": None,
#     "cession_id_list": [],
#     "profit_check": True,
#     "statistic_check": False,
# }

# {"dates_1": null,"dates_2": null,"cession_id": null,"profit_check": true,"statistic_check": false}
