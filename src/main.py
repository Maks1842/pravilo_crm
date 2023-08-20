from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserCreate, UserUpdate

from src.debts.router import router_cession, router_debtor, router_credits, router_credit_debtor, router_debtor_inn, \
    router_debt_information
from src.references.router import router_ref_status_credit
from src.collection_debt.router import router_ed_debtor

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

# Для debts
app.include_router(router_cession)
app.include_router(router_credits)
app.include_router(router_debtor)
app.include_router(router_credit_debtor)
app.include_router(router_debtor_inn)
app.include_router(router_debt_information)

# Для references
app.include_router(router_ref_status_credit)

# Для collection_debt
app.include_router(router_ed_debtor)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)