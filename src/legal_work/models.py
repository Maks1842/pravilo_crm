from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, DATE, Numeric

from src.references.models import ref_legal_section, ref_legal_docs, ref_result_statement, ref_tribunal, ref_financial_manager
from src.debts.models import credit


metadata = MetaData()

# Юридическая работа
legal_work = Table(
    "legal_work",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("legal_number", String(15), nullable=False, unique=True, doc='Уникальный номер кейса'),
    Column("legal_section_id",  Integer, ForeignKey(ref_legal_section.c.id), doc='Раздел юридической работы'),
    Column("duplicate_case", String(10), doc='Признак дубликат (описка)'),
    Column("number_case_1", String(50), doc='Номер дела (Первая инстанция)'),
    Column("legal_docs_id",  Integer, ForeignKey(ref_legal_docs.c.id), doc='Иск'),
    Column("date_session_1", DATE, doc='Дата заседания (Первая инстанция)'),
    Column("date_result_1", DATE, doc='Дата решения (Первая инстанция)'),
    Column("result_1_id",  Integer, ForeignKey(ref_result_statement.c.id), doc='Результат рассмотрения (Первая инстанция)'),
    Column("date_entry_force", DATE, doc='Дата вступления в законную силу'),
    Column("tribunal_1_id",  Integer, ForeignKey(ref_tribunal.c.id), doc='Суд (Первая инстанция)'),
    Column("summa_claim", Integer, doc='Сумма по Иску'),
    Column("date_incoming_ed", DATE, doc='Дата поступления ИД'),
    Column("date_stop_case", DATE, doc='Дата приостановки рассмотрения дела'),
    Column("summa_state_duty_claim", Integer, doc='Сумма ГП по Иску'),
    Column("summa_state_duty_result", Integer, doc='Сумма ГП по Решению'),
    Column("number_case_2", String(50), doc='Номер дела (Вторая инстанция)'),
    Column("date_session_2", DATE, doc='Дата заседания (Вторая инстанция)'),
    Column("date_result_2", DATE, doc='Дата решения (Вторая инстанция)'),
    Column("result_2_id",  Integer, ForeignKey(ref_result_statement.c.id), doc='Результат рассмотрения (Вторая инстанция)'),
    Column("tribunal_2_id",  Integer, ForeignKey(ref_tribunal.c.id), doc='Суд (Вторая инстанция)'),
    Column("date_cancel_result", DATE, doc='Дата отмены решения (СП)'),
    Column("summa_result_2", Integer, doc='Сумма по Решению 2 (Поворот)'),
    Column("date_court_costs", DATE, doc='Судебные расходы (Дата определения)'),
    Column("result_court_costs_id",  Integer, ForeignKey(ref_result_statement.c.id), doc='Результат (Судебные расходы)'),
    Column("number_ed", String(50), doc='Номер ИД'),
    Column("date_ed", DATE, doc='Дата выдачи ИД'),
    Column("summa_ed", Integer, doc='Сумма по ИД (по решению)'),
    Column("date_collection", DATE, doc='Дата взыскания'),
    Column("number_contract", String(50), doc='Номер договора (доверенности)'),
    Column("date_contract", DATE, doc='Дата договора (доверенности)'),
    Column("comment", String(200), doc='Комментарий'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Кредитный договор'),
)

# Работа с Банкротами
bankrupt_cases = Table(
    "bankrupt_cases",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("number_case", String(50), doc='Номер дела'),
    Column("date_decision", DATE, nullable=False, doc='Дата решения о признании банкротом'),
    Column("date_kommersant", String(50), doc='Дата и № публикации КоммерсантЪ'),
    Column("date_meeting", String(50), doc='Дата и время рассмотрения заявления'),
    Column("date_add_registry", DATE, doc='Дата включения в реестр'),
    Column("date_sale_property", DATE, doc='Дата реализации имущества'),
    Column("tribunal_id", Integer, ForeignKey(ref_tribunal.c.id), doc='Суд'),
    Column("financial_manager_id", Integer, ForeignKey(ref_financial_manager.c.id), doc='Финансовый управляющий'),
    Column("comment", String(200), doc='Комментарий'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Кредитный договор'),
)