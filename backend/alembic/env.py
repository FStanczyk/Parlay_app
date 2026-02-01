from alembic import context
from sqlalchemy import pool, create_engine
from app.core.database import Base
from app.core.config import settings
from app.models.user import User  # Import all models here
from app.models.bet_event import BetEvent
from app.models.tipster import Tipster
from app.models.bet_recommendation import BetRecommendation
from app.models.sport import Sport
from app.models.league import League

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with DATABASE_URL from environment
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
