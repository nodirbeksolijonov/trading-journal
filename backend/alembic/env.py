from alembic import context

import app.models  # noqa: F401  (registers the tables on Base.metadata)
from app.config import settings
from app.database import Base, make_engine

config = context.config


def run(connection):
    # Batch mode lets SQLite handle ALTERs it doesn't support natively (it rebuilds the table).
    context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=settings.database_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
elif (connection := config.attributes.get("connection")) is not None:
    # Called from app.migrate.upgrade_db with an existing connection.
    run(connection)
else:
    with make_engine(settings.database_url).begin() as connection:
        run(connection)
