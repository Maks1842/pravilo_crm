from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, DATE, Numeric


metadata = MetaData()

# Статус долга
ref_status_credit = Table(
    "ref_status_credit",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, unique=True, doc='Статус долга'),
)

# Взыскатель по ИД
ref_claimer_ed = Table(
    "ref_claimer_ed",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, unique=True, doc='Взыскатель по ИД'),
)

# Тип ИД
ref_type_ed = Table(
    "ref_type_ed",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Тип ИД'),
)

# Статус ИД
ref_status_ed = Table(
    "ref_status_ed",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, unique=True, doc='Статус ИД'),
)

# Причина отзыва ИД
ref_reason_cansel_ed = Table(
    "ref_reason_cansel_ed",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Причина отзыва ИД'),
)

# Суды
ref_tribunal = Table(
    "ref_tribunal",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False, doc='Наименование суда'),
    Column("class_code", String(9), nullable=False, unique=True, doc='Класс код суда'),
    Column("oktmo", String(50), doc='ОКТМО'),
    Column("address", String(200), doc='Адрес суда'),
    Column("email", String(100), doc='Email'),
    Column("phone", String(100), doc='Телефоны'),
    Column("gaspravosudie", Boolean, default=False, doc='Признак возможности подачи через Гасправосудие'),
)

# Финансовый управляющий
ref_financial_manager = Table(
    "ref_financial_manager",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False, unique=True, doc='Финансовый управляющий'),
    Column("organisation_fm", String(200), doc='Организация финансового управляющего'),
    Column("address_1", String(200), doc='Почтовый адрес'),
    Column("address_2", String(200), doc='Юридический адрес'),
    Column("email", String(100), doc='Email'),
    Column("phone", String(100), doc='Телефоны'),
)

# Тип департамента предъявления ИД
ref_type_department = Table(
    "ref_type_department",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Тип департамента'),
)

# Регионы
ref_region = Table(
    "ref_region",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Регион'),
    Column("index", Integer, nullable=False, unique=True, doc='Индекс региона'),
)

# Роспы
ref_rosp = Table(
    "ref_rosp",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False, unique=True, doc='РОСП'),
    Column("type_department_id", Integer, ForeignKey(ref_type_department.c.id), nullable=False, doc='Тип департамента_id'),
    Column("address", String(200), doc='Адрес'),
    Column("address_index", String(6), doc='Индекс'),
    Column("region_id", Integer, ForeignKey(ref_region.c.id), doc='Регион_id'),
    Column("phone", String(100), doc='Телефоны'),
    Column("email", String(100), doc='Email'),
    Column("class_code", String(15), unique=True, doc='Класс код РОСПа'),
)

# Банки
ref_bank = Table(
    "ref_bank",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False, unique=True, doc='Банк'),
    Column("type_department_id", Integer, ForeignKey(ref_type_department.c.id), nullable=False, doc='Тип департамента_id'),
    Column("address", String(200), doc='Адрес'),
    Column("address_index", String(6), doc='Индекс'),
    Column("region_id", Integer, ForeignKey(ref_region.c.id), doc='Регион_id'),
    Column("phone", String(100), doc='Телефоны'),
    Column("email", String(100), doc='Email'),
    Column("bik", String(9), nullable=False, unique=True, doc='БИК'),
    Column("inn", String(10), doc='ИНН'),
    Column("corr_account", String(20), doc='Корсчет'),
)

# ПФР/ИФНС
ref_pfr = Table(
    "ref_pfr",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False, unique=True, doc='ПФР/ИФНС'),
    Column("type_department_id", Integer, ForeignKey(ref_type_department.c.id), nullable=False, doc='Тип департамента_id'),
    Column("address", String(200), doc='Адрес'),
    Column("address_index", String(6), doc='Индекс'),
    Column("region_id", Integer, ForeignKey(ref_region.c.id), doc='Регион_id'),
    Column("phone", String(100), doc='Телефоны'),
    Column("email", String(100), doc='Email'),
    Column("class_code", String(15), unique=True, doc='Класс код'),
)

# Причины окончания ИП
ref_reason_end_ep = Table(
    "ref_reason_end_ep",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Причина окончания ИП'),
)

# Тип обращения
ref_type_statement = Table(
    "ref_type_statement",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Тип обращения'),
)

# Тип госпошлины
ref_type_state_duty = Table(
    "ref_type_state_duty",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Тип госпошлины'),
)

# Разделы карточки должника
ref_section_card_debtor = Table(
    "ref_section_card_debtor",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Раздел карточки должника'),
)

# Разделы юридической работы
ref_legal_section = Table(
    "ref_legal_section",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Раздел юридической работы'),
)

# Типы шаблонов документов
ref_type_templates = Table(
    "ref_type_templates",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Тип шаблона документов'),
)

# Варианты результатов/резолюций по обращениям
ref_result_statement = Table(
    "ref_result_statement",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Результат по обращению'),
    Column("type_statement_id", Integer, ForeignKey(ref_type_statement.c.id), doc='Тип обращения_id'),
)

# Наименование юридических документов
ref_legal_docs = Table(
    "ref_legal_docs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Наименование юридических документов'),
    Column("section_card_id", Integer, ForeignKey(ref_section_card_debtor.c.id), doc='Раздер карточки должника_id'),
    Column("legal_section_id", Integer, ForeignKey(ref_legal_section.c.id), doc='Раздел юридической работы_id'),
    Column("type_statement_id", Integer, ForeignKey(ref_type_statement.c.id), doc='Тип обращения_id'),
    Column("result_statement_id", Integer, ForeignKey(ref_result_statement.c.id), doc='Результат_id'),
)


# УДАЛИТЬ МОДЕЛЬ
ref_task = Table(
    "ref_task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True, doc='Задача'),
    Column("section_card_id", Integer, ForeignKey(ref_section_card_debtor.c.id), doc='Раздер карточки должника_id'),
    Column("type_statement_id", Integer, ForeignKey(ref_type_statement.c.id), doc='Тип обращения_id'),
    Column("legal_doc_id", Integer, ForeignKey(ref_legal_docs.c.id), doc='Юридический документ_id'),
    Column("result_statement_id", Integer, ForeignKey(ref_result_statement.c.id), doc='Результат_id'),
)