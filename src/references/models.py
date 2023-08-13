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
    Column("name", String(200), nullable=False, unique=True, doc='Наименование суда'),
    Column("class_code", String(9), nullable=False, unique=True, doc='Класс код суда'),
    Column("oktmo", String(50), doc='ОКТМО'),
    Column("address", String(50), doc='Адрес суда'),
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

# Департаменты предъявления ИД
ref_department_presentation = Table(
    "ref_department_presentation",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False, unique=True, doc='Департамент предъявления ИД'),
    Column("type_department_id", Integer, ForeignKey(ref_type_department.c.id), doc='Тип департамента_id'),
    Column("address", String(200), doc='Адрес департамента'),
    Column("address_index", String(6), doc='Индекс департамента'),
    Column("phone", String(100), doc='Телефоны'),
    Column("email", String(100), doc='Email'),
    Column("region_id", Integer, ForeignKey(ref_region.c.id), doc='Регион_id'),
)

# Причина окончания ИП
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