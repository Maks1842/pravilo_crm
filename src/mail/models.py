from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, DATE, JSON

from src.references.models import ref_legal_docs, ref_result_statement
from src.debts.models import credit
from src.auth.models import user


metadata = MetaData()

# Входящая корреспонденция
mail_in = Table(
    "mail_in",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("sequence_num", Integer, nullable=False, unique=True, doc='Порядковый номер'),
    Column("case_number", String(100), doc='Номер дела'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Идентификатор КД'),
    Column("barcode", String(20), doc='Штрихкод'),
    Column("date", DATE, nullable=False, doc='Дата корреспонденции'),
    Column("addresser", String(200),  nullable=False, doc='От кого'),
    Column("name_doc_id",  Integer, ForeignKey(ref_legal_docs.c.id), doc='Идентификатор наименования документа'),
    Column("resolution_id", Integer, ForeignKey(ref_result_statement.c.id), doc='Идентификатор резолюции'),
    Column("comment", String(200), doc='Комментарий'),
)


# Исходящая корреспонденция
mail_out = Table(
    "mail_out",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("sequence_num", Integer, nullable=False, unique=True, doc='Порядковый номер'),
    Column("case_number", String(100), doc='Номер дела'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Идентификатор КД'),
    Column("date", DATE, nullable=False, doc='Дата корреспонденции'),
    Column("name_doc", String(200), nullable=False, doc='Наименование документа'),
    Column("addresser", String(200),  nullable=False, doc='Адресат'),
    Column("recipient_address",  String(200),  nullable=False, doc='Адрес получателя'),
    Column("mass", Integer, doc='Масса отправления, в граммах'),
    Column("expenses_mail", Integer, doc='Почтовые расходы, в копейках'),
    Column("trek", String(20), doc='Трек номер'),
    Column("category_mail", String(20), doc='Почтовая категория'),
    Column("type_mail", JSON, doc='Тип отправления'),
    Column("type_package", String(20), doc='Тип конверт'),
    Column("barcode", String(20), doc='Штрихкод'),
    Column("num_symbol", Integer,  doc='Количество символов'),
    Column("user_id", Integer, ForeignKey(user.c.id), doc='Пользователь'),
    Column("comment", String(200), doc='Комментарий'),
)