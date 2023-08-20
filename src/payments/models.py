from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, DATE, Numeric

from src.debts.models import credit


metadata = MetaData()

# Платежи
payment = Table(
    "payment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("credit_id", Integer, ForeignKey(credit.c.id), nullable=False, doc='Кредитный договор_id'),
    Column("date", DATE, nullable=False, doc='Дата платежа'),
    Column("summa", Integer, doc='Сумма платежа'),
    Column("payment_doc_num", String(50), doc='Номер платежного документа'),
    Column("comment", String(200), doc='Комментарий'),
)