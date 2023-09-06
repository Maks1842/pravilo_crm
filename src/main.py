from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserCreate, UserUpdate

from src.debts.router import router_cession, router_credits, router_credit_debtor, router_debtor_inn, \
    router_debt_information, router_get_cession_name
from src.references.router import router_ref_status_credit, router_ref_type_templates, router_ref_task
from src.collection_debt.router import router_ed_debtor
from src.tasks.router import router_task, router_task_all

from src.registries.router import router_registry_headers, router_registry_structures, router_registry_structur_json, \
    router_registry_filters

from src.creating_docs.router import router_docs_generator_template

from src.directory_docs.router import router_dir_cession, router_docs_cession

from src.routers_helper.rout_creating_docs.generator_docs import router_generator_docs
from src.routers_helper.rout_debtor.debtor_inform import router_calculating_pensioner
from src.routers_helper.rout_admin.user_api import router_profile_user, router_list_users
from src.routers_helper.rout_debt_import.import_from_excel import router_import_headers_excel
from src.routers_helper.rout_debt_import.upload_to_database import router_post_database
from src.routers_helper.rout_registry.get_data_for_registry import router_data_registry, router_func_filters


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
app.include_router(router_ref_type_templates)
app.include_router(router_ref_task)

# Для collection_debt
app.include_router(router_ed_debtor)

# Для routers_task
app.include_router(router_task)
app.include_router(router_task_all)

# Для routers_registries
app.include_router(router_registry_headers)
app.include_router(router_registry_structures)
app.include_router(router_registry_structur_json)
app.include_router(router_registry_filters)

# Для creating_docs
app.include_router(router_docs_generator_template)
app.include_router(router_generator_docs)

# Для directory_docs
app.include_router(router_dir_cession)
app.include_router(router_docs_cession)

# Для routers_helper
app.include_router(router_calculating_pensioner)
app.include_router(router_profile_user)
app.include_router(router_list_users)
app.include_router(router_import_headers_excel)
app.include_router(router_post_database)
app.include_router(router_data_registry)
app.include_router(router_func_filters)


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