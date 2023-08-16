from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey, DATE, Numeric

from src.references.models import ref_status_credit


metadata = MetaData()

# Цессии
cession = Table(
    "cession",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, doc='Наименование цессии'),
    Column("number", String(50), nullable=False, doc='Номер цессии'),
    Column("date", DATE, doc='Дата цессии'),
    Column("summa", Numeric(12, 2), doc='Сумма цессии'),
    Column("cedent", String(100), doc='Цедент'),
    Column("cessionari", String(100), doc='Цессионарий'),
    Column("date_old_cession", String(100), doc='Даты предыдущих цессий'),
)

# Должники
debtor = Table(
    "debtor",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("last_name_1", String(80), nullable=False, doc='Фамилия должника (по договору)'),
    Column("first_name_1", String(20), nullable=False, doc='Имя должника (по договору)'),
    Column("second_name_1", String(20), doc='Отчество должника (по договору)'),
    Column("last_name_2", String(80), doc='Фамилия должника (изменения)'),
    Column("first_name_2", String(20), doc='Имя должника (изменения)'),
    Column("second_name_2", String(20), doc='Отчество должника (изменения)'),
    Column("pol", String(10), nullable=False, doc='Пол'),
    Column("birthday", DATE, doc='Дата рождения'),
    Column("pensioner", Boolean, default=False, doc='Признак пенсионера'),
    Column("place_of_birth", String(200), doc='Место рождения'),
    Column("passport_series", String(5), doc='Серия паспорта'),
    Column("passport_num", String(6), doc='Номер паспорта'),
    Column("passport_date", DATE, doc='Дата выдачи паспорта'),
    Column("passport_department", String(200), doc='Кем выдан паспорт'),
    Column("inn", String(12), doc='ИНН'),
    Column("snils", String(14), doc='СНИЛС'),
    Column("address_1", String(200), doc='Адрес прописки'),
    Column("address_2", String(200), doc='Адрес проживания'),
    Column("index_add_1", String(6), doc='Индекс прописки'),
    Column("index_add_2", String(6), doc='Индекс проживания'),
    Column("phone", String(100), doc='Телефоны'),
    Column("email", String(100), doc='Эл. почта'),
    Column("comment", String(200), doc='Комментарий'),
)

# Кредиты
credit = Table(
    "credit",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("creditor", String(100), nullable=False, doc='Кредитор'),
    Column("number", String(50), nullable=False, doc='Номер кредитного договора'),
    Column("date_start", DATE, doc='Дата выдачи КД'),
    Column("date_end", String(100), doc='Срок КД'),
    Column("summa_by_cession", Numeric(12, 2), doc='Сумма по цессии'),
    Column("summa", Numeric(12, 2), doc='Сумма КД'),
    Column("interest_rate", Numeric(5, 2), doc='Процентная ставка по КД'),
    Column("overdue_od", Boolean, default=False, doc='Просроченный ОД'),
    Column("overdue_percent", Numeric(12, 2), doc='Просроченные проценты'),
    Column("penalty", Numeric(12, 2), doc='Штрафы, пени'),
    Column("percent_of_od", Numeric(12, 2), doc='Проценты на ОД'),
    Column("gov_toll", Numeric(12, 2), doc='Госпошлина'),
    Column("balance_debt", Numeric(12, 2), doc='Остаток долга'),
    Column("debtor_id", Integer, ForeignKey(debtor.c.id), doc='Должник_id'),
    Column("cession_id", Integer, ForeignKey(cession.c.id), doc='Цессия_id'),
    Column("status_cd_id", Integer, ForeignKey(ref_status_credit.c.id), doc='Статус долга_id'),
    Column("comment", String(200), doc='Комментарий'),
    Column("credits_old", String(100), doc='Старые кредиты'),
)