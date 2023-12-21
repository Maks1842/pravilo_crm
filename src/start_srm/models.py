from sqlalchemy import MetaData, Table, Column, Integer, DATE


metadata = MetaData()

# Статус долга
date_start_functions = Table(
    "date_start_functions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("date", DATE, doc='Дата запуска функций'),
    Column("number_days", Integer, doc='Количество дней для задержки'),
)