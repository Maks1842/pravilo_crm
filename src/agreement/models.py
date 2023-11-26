from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, DATE, JSON
from src.debts.models import credit


metadata = MetaData()

# Соглашения
agreement = Table(
    "agreement",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Идентификатор КД'),
    Column("number",  String(50), doc='Номер соглашения'),
    Column("date", DATE, doc='Дата соглашения'),
    Column("summa", Integer, doc='Сумма соглашения'),
    Column("payment_schedule", JSON, nullable=False, doc='График платежей JSON'),
    Column("comment", String(200), doc='Комментарий'),
)