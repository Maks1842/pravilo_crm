from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

from src.debts.models import cession, credit


metadata = MetaData()

# Директория и Документы по Цессиям
dir_cession = Table(
    "dir_cession",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False, doc='Наименование цессии'),
    Column("cession_id", Integer, ForeignKey(cession.c.id), doc='Цессия_id'),
    Column("path", String(200), doc='Путь к папке с Цессией'),
)

# Директория и Документы по Кредитам
dir_credit = Table(
    "dir_credit",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False, doc='Наименование досье кредита'),
    Column("credit_id", Integer, ForeignKey(credit.c.id), doc='Кредит_id'),
    Column("path", String(200), doc='Путь к папке с Досье по кредиту'),
)

# Папки в досье
dir_folder = Table(
    "dir_folder",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False, doc='Наименование папки в досье'),
)

# Документы в папках досье
docs_folder = Table(
    "docs_folder",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False, doc='Документ в папке досье'),
    Column("folder_id", Integer, ForeignKey(dir_folder.c.id), doc='Папка_id'),
)

# Досье
dir_form = Table(
    "dir_form",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("credit_dir_id", Integer, ForeignKey(dir_credit.c.id), doc='Директория досье_id'),
    Column("docs_folder_id", Integer, ForeignKey(docs_folder.c.id), doc='Документ_id'),
    Column("path", String(200), doc='Путь к документу'),
)