from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserCreate, UserUpdate

from src.debts.router import router_lending, router_cession, router_credits, router_debtor, router_credit_debtor, router_debtor_inn, \
    router_debt_information, router_get_cession_name, router_get_lending_name, router_debtor_name
from src.references.router import router_ref_status_credit, router_ref_claimer_ed, router_ref_type_ed, router_ref_type_templates, \
    router_ref_status_ed, router_ref_reason_cansel_ed, router_ref_tribunal,  router_ref_financial_manager, router_ref_type_department, \
    router_ref_region, router_ref_rosp, router_ref_bank, router_ref_pfr, router_ref_reason_end_ep, router_ref_type_statement, \
    router_ref_type_state_duty, router_ref_section_card_debtor, router_ref_legal_section, router_ref_legal_docs, \
    router_ref_result_statement, router_ref_type_filters

from src.collection_debt.routers.collection_debt_rout import router_collection_debt, router_department_presentation
from src.collection_debt.routers.executive_document_rout import router_ed_debtor, router_ed_number
from src.collection_debt.routers.executive_productions_rout import router_ep_debtor, router_ep_number
from src.legal_work.routers.tribunal_write_rout import router_tribunal_write
from src.legal_work.routers.succession_rout import router_succession
from src.legal_work.routers.state_duty_calculation import router_duty_legal_calculation
from src.legal_work.routers.calculation_debt_for_tribunal import router_calculation_debt, router_calculation_annuity_payment

from src.tasks.router import router_task, router_task_all

from src.registries.router import router_registry_headers, router_registry_structures, router_registry_structur_json, \
    router_registry_filters

from src.creating_docs.router import router_docs_generator_template

from src.directory_docs.router import router_dir_cession, router_docs_cession, router_download_file_cession, \
    router_dir_credit, router_docs_credit, router_defolt_docs, router_download_file_credit, router_rename_file

from src.mail.routers.incoming_mail import router_incoming_mail
from src.mail.routers.outgoing_mail import router_outgoing_mail, router_mail_to_excel

from src.routers_helper.rout_creating_docs.generator_docs import router_generator_docs
from src.routers_helper.rout_creating_docs.generator_txt import router_generator_txt
from src.routers_helper.rout_calculator.debtor_inform import router_calculating_pensioner
from src.routers_helper.rout_admin.user_api import router_profile_user, router_list_users
from src.routers_helper.rout_debt_import.import_from_excel import router_import_headers_excel
from src.routers_helper.rout_debt_import.upload_to_database import router_post_database
from src.routers_helper.rout_registry.get_data_for_registry import router_data_registry, router_func_filters
from src.routers_helper.rout_registry.registry_outgoing_mail import router_reg_outgoing_mail
from src.routers_helper.rout_admin.helper_helper import router_helper

from src.finance.routers.expenses_rout import router_expenses_category, router_expenses
from src.finance.routers.reports_rout import router_report_parent_organisation, router_report_for_investor

from src.payments.routers.payments import router_payment, router_post_payment_list
from src.payments.routers.extract_payments import router_extract_payments

from src.agreement.routers.agreements import router_agreement


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
app.include_router(router_lending)
app.include_router(router_cession)
app.include_router(router_get_cession_name)
app.include_router(router_credits)
app.include_router(router_debtor)
app.include_router(router_credit_debtor)
app.include_router(router_debtor_inn)
app.include_router(router_debtor_name)
app.include_router(router_debt_information)
app.include_router(router_get_lending_name)

# Для references
app.include_router(router_ref_status_credit)
app.include_router(router_ref_claimer_ed)
app.include_router(router_ref_type_ed)
app.include_router(router_ref_type_templates)
app.include_router(router_ref_status_ed)
app.include_router(router_ref_reason_cansel_ed)
app.include_router(router_ref_tribunal)
app.include_router(router_ref_financial_manager)
app.include_router(router_ref_type_department)
app.include_router(router_ref_region)
app.include_router(router_ref_rosp)
app.include_router(router_ref_bank)
app.include_router(router_ref_pfr)
app.include_router(router_ref_reason_end_ep)
app.include_router(router_ref_type_statement)
app.include_router(router_ref_type_state_duty)
app.include_router(router_ref_section_card_debtor)
app.include_router(router_ref_legal_docs)
app.include_router(router_ref_legal_section)
app.include_router(router_ref_result_statement)
app.include_router(router_ref_type_filters)

# Для collection_debt
app.include_router(router_ed_debtor)
app.include_router(router_collection_debt)
app.include_router(router_ed_number)
app.include_router(router_department_presentation)
app.include_router(router_ep_debtor)
app.include_router(router_ep_number)

# Для legal_work
app.include_router(router_tribunal_write)
app.include_router(router_succession)
app.include_router(router_duty_legal_calculation)
app.include_router(router_calculation_debt)
app.include_router(router_calculation_annuity_payment)

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
app.include_router(router_download_file_cession)
app.include_router(router_download_file_credit)
app.include_router(router_dir_credit)
app.include_router(router_docs_credit)
app.include_router(router_defolt_docs)
app.include_router(router_rename_file)

# Для mail
app.include_router(router_incoming_mail)
app.include_router(router_outgoing_mail)
app.include_router(router_mail_to_excel)

# Для routers_helper
app.include_router(router_calculating_pensioner)
app.include_router(router_profile_user)
app.include_router(router_list_users)
app.include_router(router_import_headers_excel)
app.include_router(router_post_database)
app.include_router(router_data_registry)
app.include_router(router_func_filters)
app.include_router(router_reg_outgoing_mail)
app.include_router(router_helper)
app.include_router(router_generator_txt)

# Для finance
app.include_router(router_expenses_category)
app.include_router(router_expenses)
app.include_router(router_report_parent_organisation)
app.include_router(router_report_for_investor)

# Для payment
app.include_router(router_payment)
app.include_router(router_post_payment_list)
app.include_router(router_extract_payments)

# Для agreement
app.include_router(router_agreement)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8080/",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)