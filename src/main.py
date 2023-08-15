from fastapi import FastAPI
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserCreate, UserUpdate

from src.debts.router import router_cession, router_debtor

app = FastAPI(
    title="Pravilo_CRM"
)

# Роутер для аутентификации
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

# Роутер для регистрации
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

# Роутер для управления пользователями
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["Users"],
)

app.include_router(router_cession)
app.include_router(router_debtor)