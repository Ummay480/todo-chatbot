import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from src.database.connection import DATABASE_URL, Base

# Import all models to register them with the Base metadata
from src.models.User import User
from src.models.LedgerPage import LedgerPage
from src.models.SalesEntry import SalesEntry
from src.models.DailyReport import DailyReport
from src.models.MonthlyReport import MonthlyReport
from src.models.ColumnDefinition import ColumnDefinition
from src.models.UserPreferences import UserPreferences

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Set the sqlalchemy.url from the environment variable
config.set_main_option('sqlalchemy.url', DATABASE_URL)


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
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # For autogenerate, we don't need to connect to a real database
    # Just configure the context with the target metadata
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


# Always use offline mode for autogenerate to avoid needing a live database connection
if context.is_offline_mode() or context.get_x_argument(as_dictionary=True).get('autogen', False):
    run_migrations_offline()
else:
    run_migrations_online()