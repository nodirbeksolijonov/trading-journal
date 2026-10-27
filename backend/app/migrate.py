from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine, inspect

from app.database import engine as default_engine

BACKEND_DIR = Path(__file__).resolve().parent.parent


def upgrade_db(engine: Engine = default_engine) -> None:
    """Bring the database schema up to date. Runs on every app start, in one transaction."""
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    with engine.begin() as connection:
        cfg.attributes["connection"] = connection
        current = MigrationContext.configure(connection).get_current_revision()
        if current is None and inspect(connection).has_table("trades"):
            # Database was made by create_all before migrations existed: it matches 0001.
            command.stamp(cfg, "0001")
        command.upgrade(cfg, "head")
