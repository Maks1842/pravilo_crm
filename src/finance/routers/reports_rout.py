from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_async_session
from src.finance.routers.reports_functions import get_revenue, get_statistic
from src.debts.models import cession
from src.routers_helper.data_to_excel.statistic_to_excel import statistic_to_excel_organisation, statistic_to_excel_investor


# Получить отчеты по головной организации
router_report_parent_organisation = APIRouter(
    prefix="/v1/ReportParentOrganisation",
    tags=["Finance"]
)


@router_report_parent_organisation.post("/")
async def report_parent_organisation(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    # test_result = await get_statistic(data_json, session)
    # return test_result

    profit_check = data_json['profit_check']
    statistic_check = data_json['statistic_check']

    if 'date_1' not in data_json:
        data_json["date_1"] = None
    if 'date_2' not in data_json:
        data_json["date_2"] = None

    data_json["cession_array"] = []

    if profit_check:
        try:
            # result = await get_revenue(data_json, session)

            print('Заглушка')

            return {
                'status': 'success',
                'data': None,
                'details': f'Данная функция в разработке'
            }
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": ex
            }
    elif statistic_check:
        try:
            data_statistic = await get_statistic(data_json, session)

            result = statistic_to_excel_organisation(data_statistic)

            return result
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

    cession_query = await session.execute(select(cession).where(cession.c.lending_id == lending_id))
    data_json["cession_array"] = cession_query.mappings().all()


    if 'date_1' not in data_json:
        data_json["date_1"] = None
    if 'date_2' not in data_json:
        data_json["date_2"] = None

    if profit_check:

        try:
            # result = await get_revenue(data_json, session)
            print('Заглушка')

            return {
                'status': 'success',
                'data': None,
                'details': f'Данная функция в разработке'
            }
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": ex
            }

    elif statistic_check:
        try:
            data_statistic = await get_statistic(data_json, session)

            result = statistic_to_excel_investor(data_statistic)

            return result
        except Exception as ex:
            return {
                "status": "error",
                "data": None,
                "details": ex
            }


# data_json: {
#     "date_1": None,
#     "date_2": None,
#     "cession_id_list": [],
#     "profit_check": True,
#     "statistic_check": False,
# }

# {"date_1": null,"date_2": null,"cession_id": null,"profit_check": false,"statistic_check": true}
