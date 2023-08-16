from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from datetime import datetime
from fastapi_users.db import SQLAlchemyBaseUserTable

from src.database import Base

'''
Создаю необходимые модели, далее запускаю миграции:
1. $ alembic init migrations - создать директорию для миграций (единоразово)
2. В файл migrations.env.py - импортировать директорию, из которой будут осуществляться миграции 
3. $ alembic revision --autogenerate -m "Database creation" - создать миграцию, сравнивает текущее состояние в БД с тем, что есть на сервере
4.1 $ alembic upgrade c67289f4ce04 - Применяю миграции (создаю таблицы в БД), указывая хэш (находится в конкретном файле миграции) до какой миграции надо обновиться или
4.2 $ alembic upgrade head - Применяю миграции (создаю таблицы в БД), применить до последней миграции

$ uvicorn src.main:app --reload - Старт проекта
'''

metadata = MetaData()

# Императивный подход в описании Моделей (типа удобнее работать с миграциями и ORM)
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


# Декларативный подход в описании Моделей
class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    last_name = Column(String(length=20), nullable=False)
    first_name = Column(String(length=50), nullable=False)
    birthday = Column(TIMESTAMP)
    date_registered = Column(TIMESTAMP, default=datetime.utcnow)
    email: str = Column(String(length=320), unique=True, index=True, nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


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