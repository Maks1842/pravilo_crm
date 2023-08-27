from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, JSON
from src.registries.models import registry_headers
from src.references.models import ref_type_templates


metadata = MetaData()


# Типы сущностей склоняемого слова
docs_generator_entity = Table(
    "docs_generator_entity",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("entity_name", String(50), nullable=False, unique=True, doc='Сущность склоняемого слова'),
)


# Переменные для генератора документов
docs_generator_variable = Table(
    "docs_generator_variable",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("variables", String(50), nullable=False, doc='Наименование модели БД'),
    Column("entity_id", Integer, ForeignKey(docs_generator_entity.c.id), doc='Тип сущности склоняемого слова'),
    Column("registry_headers_id", Integer, ForeignKey(registry_headers.c.id), doc='Идентификатор KEY столбцов реестров'),
)


# Склонения для печатных форм
docs_generator_declension = Table(
    "docs_generator_declension",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("entity_id", Integer, ForeignKey(docs_generator_entity.c.id), doc='Тип сущности склоняемого слова'),
    Column("number_word", Integer, doc='Номер слова которое необходимо склонять'),
    Column("ending_word", String(20), doc='Окончание склоняемого слова'),
    Column("gender", String(10), doc='Род муж/жен'),
    Column("imenit", String(10), doc='Именительный падеж'),
    Column("rodit", String(10), doc='Родительный падеж'),
    Column("datel", String(10), doc='Дательный падеж'),
    Column("vinit", String(10), doc='Винительный падеж'),
    Column("tvorit", String(10), doc='Творительный падеж'),
    Column("predl", String(10), doc='Предложный падеж'),
)


# Шаблоны печатных форм
docs_generator_template = Table(
    "docs_generator_template",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, doc='Наименование модели БД'),
    Column("type_template_id", Integer, ForeignKey(ref_type_templates.c.id), doc='Тип шаблона'),
    Column("path_template_file", String(200), nullable=False, unique=True, doc='Путь к файлу шаблона'),
)