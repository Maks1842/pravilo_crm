from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, JSON


metadata = MetaData()

# Заголовки столбцов реестра должников
registry_headers = Table(
    "registry_headers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("model", String(50), nullable=False, doc='Наименование модели БД'),
    Column("name_field", String(50), nullable=False, doc='Наименование поля в Модели'),
    Column("headers", String(100), nullable=False, unique=True, doc='Заголовок столбца в таблице frontend'),
    Column("headers_key", String(50), nullable=False, doc='Ключ заголовка столбца (поля модели)'),
    Column("width_field", Integer, doc='Ширина столбца'),
    Column("employ_registry", Boolean, default=True, nullable=False, doc='Признак использования поля в реестрах/таблицах'),
)


# Справочник реестров должников
registry_structures = Table(
    "registry_structures",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Наименование структуры'),
    Column("items_json", JSON,  nullable=False, doc='Структура'),
)


# Фильтры контроля для реестра
registry_filters = Table(
    "registry_filters",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Наименование фильтра'),
    Column("function_name", String(50), doc='Название функции'),
    Column("registry_structure_id", Integer, ForeignKey(registry_structures.c.id), doc='Идентификатор структуры реестра'),
)