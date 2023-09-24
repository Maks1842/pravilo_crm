from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

from src.debts.models import cession, credit


metadata = MetaData()

# Директории по Цессиям
dir_cession = Table(
    "dir_cession",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False, doc='Наименование цессии'),
    Column("cession_id", Integer, ForeignKey(cession.c.id), doc='Цессия_id'),
    Column("path", String(200), doc='Путь к папке с Цессией'),
)

# Документы по Цессиям
docs_cession = Table(
    "docs_cession",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, doc='Наименование документа'),
    Column("dir_cession_id", Integer, ForeignKey(dir_cession.c.id), doc='Директория цессии'),
    Column("path", String(200), doc='Путь к документу'),
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

# Папки в досье КД
dir_folder = Table(
    "dir_folder",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, doc='Наименование папки в досье'),
)

# Дефолтные наименования документов в папках досье
defolt_docs = Table(
    "defolt_docs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False, doc='Дефолтное наименование документа'),
    Column("folder_id", Integer, ForeignKey(dir_folder.c.id), doc='Папка_id'),
)

# Документы по КД
docs_folder = Table(
    "docs_folder",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(150), nullable=False, doc='Наименование документа'),
    Column("name_folder", String(100), doc='Наименование папки'),
    Column("dir_credit_id", Integer, ForeignKey(dir_credit.c.id), doc='Директория досье_id'),
    Column("path", String(200), doc='Путь к документу'),
)