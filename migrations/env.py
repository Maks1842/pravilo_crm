from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from src.auth.models import metadata as metadata_auth
from src.debts.models import metadata as metadata_debts
from src.references.models import metadata as metadata_references
from src.directory_docs.models import metadata as directory_docs
from src.collection_debt.models import metadata as collection_debt
from src.legal_work.models import metadata as legal_work
from src.payments.models import metadata as payments
from src.tasks.models import metadata as tasks
from src.registries.models import metadata as registries
from src.creating_docs.models import metadata as creating_docs
from src.mail.models import metadata as mail
from src.finance.models import metadata as finance
from src.agreement.models import metadata as agreement
from src.start_srm.models import metadata as date_start_functions

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

import os
import sys

sys.path.append(os.path.join(sys.path[0], 'src'))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
config.set_section_option(section, 'DB_NAME', DB_NAME)
config.set_section_option(section, 'DB_USER', DB_USER)
config.set_section_option(section, 'DB_PASS', DB_PASS)
config.set_section_option(section, 'DB_HOST', DB_HOST)
config.set_section_option(section, 'DB_PORT', DB_PORT)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = [metadata_auth, metadata_debts, metadata_references, directory_docs, collection_debt, legal_work,
                   payments, tasks, registries, creating_docs, mail, finance, agreement, date_start_functions]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
