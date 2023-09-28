from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, DATE, Numeric

from src.debts.models import cession


metadata = MetaData()


# Категории расходов
ref_expenses_category = Table(
    "ref_expenses_category",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, unique=True, doc='Наименование категории'),
)


# Расходы
expenses = Table(
    "expenses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("date", DATE, nullable=False, doc='Дата платежа'),
    Column("summa", Integer, doc='Сумма платежа'),
    Column("expenses_category_id",  Integer, ForeignKey(ref_expenses_category.c.id), doc='Категория расходов'),
    Column("payment_purpose", String(150), doc='Назначение платежа'),
    Column("cession_id", Integer, ForeignKey(cession.c.id), doc='Цессия_id'),
)


