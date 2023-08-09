from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, JSON
from datetime import datetime

'''
Создаю необходимые модели, далее запускаю миграции:
1. $ alembic init migrations - создать директорию для миграций (единоразово)
2. $ alembic revision --autogenerate -m "Database creation" - создать миграцию, сравнивает текущее состояние в БД с тем, что есть на сервере
3.1 $ alembic upgrade c67289f4ce04 - Применяю миграции (создаю таблицы в БД), указывая хэш (находится в конкретном файле миграции) до какой миграции надо обновиться или
3.2 $ alembic upgrade head - Применяю миграции (создаю таблицы в БД), применить до последней миграции
'''

metadata = MetaData()

# Пользователи
user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(20), nullable=False, unique=True),
    Column("hashed_password", String, nullable=False),
    Column("is_superuser", Boolean),
    Column("last_name", String(20), nullable=False),
    Column("first_name", String(50), nullable=False),
    Column("birthday", TIMESTAMP),
    Column("date_registered", TIMESTAMP, default=datetime.utcnow),
    Column("email", String),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False)
)

# Отделы
department = Table(
    "department",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, unique=True),
)

# Роли/должности
role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, unique=True),
)

# Профили пользователей
profile = Table(
    "profile",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(user.c.id)),
    Column("department_id", Integer, ForeignKey(department.c.id)),
    Column("role_id", Integer, ForeignKey(role.c.id)),
)