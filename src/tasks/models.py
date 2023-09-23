from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, DATE, Numeric

from src.references.models import ref_legal_docs, ref_section_card_debtor, ref_result_statement, ref_type_statement
from src.debts.models import credit
from src.auth.models import user


metadata = MetaData()

# Задачи
task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name_id", Integer, ForeignKey(ref_legal_docs.c.id), nullable=False, doc='Задача'),
    Column("section_card_debtor_id", Integer, ForeignKey(ref_section_card_debtor.c.id), doc='Раздел карточки должника'),
    Column("type_statement_id", Integer, ForeignKey(ref_type_statement.c.id), doc='Тип обращения'),
    Column("date_task", DATE, doc='Дата начала'),
    Column("timeframe", String(20), doc='Срок выполнения'),
    Column("user_id", Integer, ForeignKey(user.c.id), doc='Ответственный сотрудник'),
    Column("date_statement", DATE, doc='Дата подачи обращения'),
    Column("track_num", String(50), doc='Трэк номер'),
    Column("date_answer", DATE, doc='Дата получения ответа'),
    Column("result_id", Integer, ForeignKey(ref_result_statement.c.id), doc='Результат'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Кредитный договор'),
    Column("comment", String(200), doc='Комментарий'),
)