from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.finance.models import ref_expenses_category, expenses
from src.finance.routers.reports_functions import get_revenue

import math
from datetime import datetime


# Получить отчеты по головной организации
router_report_parent_organisation = APIRouter(
    prefix="/v1/ReportParentOrganisation",
    tags=["Finance"]
)


@router_report_parent_organisation.post("/")
async def report_parent_organisation(data_json: dict, session: AsyncSession = Depends(get_async_session)):


    profit_check = data_json['data_json']['profit_check']
    statistic_check = data_json['data_json']['statistic_check']

    if profit_check:

        try:
            result = await get_revenue(data_json, session)

            return result
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
