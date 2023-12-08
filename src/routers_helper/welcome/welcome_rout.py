import random

from fastapi import APIRouter
from src.variables_for_front import welcome_list
from src.variables_for_front import VariablesFront


# Роутер для приветствия
router_welcome = APIRouter(
    prefix="/v1/GetWelcomeText",
    tags=["Admin"]
)

@router_welcome.get("/")
async def get_welcome_text():

    result = random.choice(welcome_list)

    return result


# Роутер для экспортирования переменных на Фронт
router_export_variables = APIRouter(
    prefix="/v1/GetExportVariables",
    tags=["Admin"]
)

@router_export_variables.get("/")
async def export_variables():

    return VariablesFront.variables


