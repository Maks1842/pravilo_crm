from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserCreate, UserUpdate

from src.debts.router import router_cession, router_credits, router_credit_debtor, router_debtor_inn, \
    router_debt_information, router_get_cession_name
from src.references.router import router_ref_status_credit
from src.collection_debt.router import router_ed_debtor
from src.tasks.router import router_task, router_task_all

from src.routers_helper.rout_debtor.debtor_inform import router_calculating_pensioner
from src.routers_helper.rout_admin.user_api import router_profile_user, router_list_users
from src.routers_helper.rout_debt_import.import_from_excel import router_import_headers_excel

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
app.include_router(router_get_cession_name)
app.include_router(router_credits)
app.include_router(router_credit_debtor)
app.include_router(router_debtor_inn)
app.include_router(router_debt_information)

# Для references
app.include_router(router_ref_status_credit)

# Для collection_debt
app.include_router(router_ed_debtor)

# Для routers_helper
app.include_router(router_calculating_pensioner)
app.include_router(router_profile_user)
app.include_router(router_list_users)
app.include_router(router_import_headers_excel)

# Для routers_task
app.include_router(router_task)
app.include_router(router_task_all)


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