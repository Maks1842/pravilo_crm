from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from fastapi_users import fastapi_users

from auth.auth import auth_backend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate, UserUpdate

app = FastAPI(
    title="Pravilo_CRM"
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Роутер для аутентификации
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Роутер для регистрации
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Роутер для управления пользователями
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

#
# fake_users = [
#     {"id": 1, "username": "admin", "password": "123456", "is_superuser": True, "last_name": "Ivanov", "first_name": "Ivan" },
#     {"id": 2, "username": "user1", "password": "22222", "is_superuser": False, "last_name": "Igor", "first_name": "Tany" },
# ]
#
#
# class User(BaseModel):
#     id: int
#     username: str = Field(max_length=10)
#     password: str = Field(max_length=10)
#     is_superuser: bool
#     last_name: str
#     first_name: str
#     second_name: Optional[str] = None
#     birthday: Optional[datetime] = None
#     date_joined: Optional[datetime] = None
#     email: Optional[str] = None
#
#
# @app.get("/users/{user_id}", response_model=List[User])
# def get_user(user_id: int):
#     for user in fake_users:
#         if user.get('id') == user_id:
#             return [user]
#
#
# @app.post("/users")
# def add_user(users: List[User]):
#     fake_users.extend(users)
#     return {"status": 200, "data": fake_users}