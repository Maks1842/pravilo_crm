from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert, func, distinct, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.auth.models import user


# Получить профиль пользователя
router_profile_user = APIRouter(
    prefix="/v1/GetProfileUser",
    tags=["Admin"]
)

@router_profile_user.get("/")
async def get_profile_user(email: str = None, user_id: int = None, session: AsyncSession = Depends(get_async_session)):

    try:
        if email:
            user_query = await session.execute(select(user).where(user.c.email.ilike(email)))
        else:
            user_query = await session.execute(select(user).where(user.c.id == user_id))

        user_item = dict(user_query.one()._mapping)

        result = {
            "user_id": user_item['id'],
            "username": user_item['username'],
            "superuser": user_item['is_superuser'],
            "first_name": user_item['first_name'],
            "last_name": user_item['last_name'],
            "name_full": f'{user_item["first_name"]} {user_item["last_name"] or ""}',
            "birthday": user_item['birthday'],
            "email": user_item['email'],
        }

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }


# Получить списки юзеров
router_list_users = APIRouter(
    prefix="/v1/GetListUsers",
    tags=["Admin"]
)

@router_list_users.get("/")
async def get_list_users(session: AsyncSession = Depends(get_async_session)):

    try:
        query = await session.execute(select(user))

        result = []
        for item in query.all():
            item_dic = dict(item._mapping)

            result.append({
                "user_name_full": f'{item_dic["first_name"]} {item_dic["last_name"] or ""}',
                "value": {
                    "user_id": item_dic["id"],
                },
            })

        return result
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": ex
        }