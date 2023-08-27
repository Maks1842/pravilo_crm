from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, DATE, Numeric

from src.references.models import ref_claimer_ed, ref_tribunal, ref_type_ed, ref_status_ed, ref_reason_end_ep, \
    ref_rosp, ref_type_department, ref_reason_cansel_ed
from src.debts.models import credit, debtor
from src.auth.models import user


metadata = MetaData()

# Исполнительные документы
executive_document = Table(
    "executive_document",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("number", String(50), nullable=False, doc='Номер ИД'),
    Column("date", DATE, nullable=False, doc='Дата ИД'),
    Column("case_number", String(100), doc='Номер дела'),
    Column("date_of_receipt_ed", DATE, doc='Дата выдачи ИД'),
    Column("date_decision", DATE, doc='Дата принятия решения'),
    Column("type_ed_id", Integer, ForeignKey(ref_type_ed.c.id), doc='Тип ИД_id'),
    Column("status_ed_id", Integer, ForeignKey(ref_status_ed.c.id), doc='Статус ИД_id'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Кредитный договор_id'),
    Column("user_id", Integer, ForeignKey(user.c.id), doc='Ответственный сотрудник'),
    Column("summa_debt_decision", Integer, doc='Долг по решению суда'),
    Column("state_duty", Integer, doc='Госпошлина'),
    Column("succession", DATE, doc='Дата процессуального правопреемства'),
    Column("date_entry_force", DATE, doc='Дата вступления в законную силу'),
    Column("claimer_ed_id", Integer, ForeignKey(ref_claimer_ed.c.id), doc='Взыскатель по ИД_id'),
    Column("tribunal_id", Integer, ForeignKey(ref_tribunal.c.id), doc='Суд выдавший ИД_id'),
    Column("comment", String(200), doc='Комментарий'),
)

# Исполнительное производство
executive_productions = Table(
    "executive_productions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("number", String(50), nullable=False, doc='Номер исполнительного производства'),
    Column("summary_case", String(50), doc='Сводное дело'),
    Column("date_on", DATE, doc='Дата возбуждения ИП'),
    Column("date_end", DATE, doc='Дата окончания ИП'),
    Column("reason_end_id", Integer, ForeignKey(ref_reason_end_ep.c.id), doc='Причина окончания_id'),
    Column("curent_debt", Integer, doc='Текущая задолженность'),
    Column("summa_debt", Integer, doc='Основной долг'),
    Column("gov_toll", Integer, doc='Исполнительский сбор'),
    Column("rosp_id", Integer, ForeignKey(ref_rosp.c.id), doc='РОСП_id'),
    Column("pristav", String(50), doc='Пристав'),
    Column("pristav_phone", String(50), doc='Телефон пристава'),
    Column("date_request", DATE, doc='Дата получения данных из РОСП'),
    Column("object_ep", String(100), doc='Предмет исполнительного производства'),
    Column("executive_document_id", Integer, ForeignKey(executive_document.c.id), doc='Исполнительный документ_id'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Кредитный договор_id'),
    Column("claimer", String(100), doc='Взыскатель'),
    Column("comment", String(200), doc='Комментарий'),
)

# Департамент предъявления ИД
department_presentation = Table(
    "department_presentation",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("department_presentation_id", Integer, nullable=False, doc='Учреждение предъявления_id'),
    Column("type_department_id", Integer, ForeignKey(ref_type_department.c.id), nullable=False, doc='Тип департамента_id'),
)

# Движение исполнительного документа
collection_debt = Table(
    "collection_debt",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("department_presentation_id", Integer, ForeignKey(department_presentation.c.id), nullable=False, doc='Учреждение предъявления_id'),
    Column("executive_document_id", Integer, ForeignKey(executive_document.c.id), doc='Исполнительный документ_id'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Кредитный договор_id'),
    Column("date_start", DATE, doc='Дата предъявления ИД'),
    Column("date_return", DATE, doc='Дата отзыва ИД'),
    Column("date_end", DATE, doc='Дата возврата ИД'),
    Column("reason_cansel_id", Integer, ForeignKey(ref_reason_cansel_ed.c.id), doc='Причина отзыва ИД_id'),
    Column("comment", String(200), doc='Комментарий'),
)

# Сведения из ИФНС
ifns_information = Table(
    "ifns_information",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("date_inform", DATE, nullable=False, doc='Дата сведений'),
    Column("debtor_id", Integer, ForeignKey(debtor.c.id), doc='Должник_id'),
    Column("birthday", DATE, doc='Дата рождения'),
    Column("inn", String(15), doc='ИНН должника'),
)

# ИФНС о банковских счетах
ifns_bank_account = Table(
    "ifns_bank_account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("ifns_inform_id", Integer, ForeignKey(ifns_information.c.id), doc='Сведения из ИФНС_id'),
    Column("debtor", Integer, ForeignKey(debtor.c.id), doc='Должник_id'),
    Column("bank", String(150), doc='Банк'),
    Column("bik", String(9), doc='БИК'),
    Column("inn", String(10), doc='ИНН'),
    Column("account_number", String(20), doc='Номер счета'),
    Column("date_account", DATE, doc='Дата открытия счета'),
)