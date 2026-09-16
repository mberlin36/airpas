from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlmodel import SQLModel

# Import all models so they are registered with SQLModel.metadata
from airpas.models import *  # noqa: F403, F401, E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set database URL from environment variable if present
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = SQLModel.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects to include/exclude during autogeneration.
    """
    if type_ == "table" and object.info.get("skip_autogenerate", False):
        return False

    elif type_ == "column" and object.info.get("skip_autogenerate", False):
        return False

    return True


def include_name(name, type_, parent_names):
    """
    Filter tables so Alembic only manages tables defined in SQLModel metadata,
    ignoring system, extension, or unmanaged postgres tables.
    """
    if type_ == "table":
        # Ignore postgres system schemas/tables and spatial tables
        if name in ("spatial_ref_sys", "geography_columns", "geometry_columns"):
            return False
        if name.startswith("pg_") or name.startswith("sql_"):
            return False
        return name in target_metadata.tables
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
        compare_server_default=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
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
            include_object=include_object,
            compare_server_default=True,
            include_name=include_name,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
