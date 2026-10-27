from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def make_engine(url: str, **kwargs) -> Engine:
    if not url.startswith("sqlite"):
        return create_engine(url, **kwargs)

    # SQLite needs check_same_thread=False because FastAPI may use a session from a different thread.
    engine = create_engine(url, connect_args={"check_same_thread": False}, **kwargs)

    # Python's sqlite3 commits DDL (CREATE/ALTER/DROP) immediately instead of inside the
    # transaction, so a failed migration would be left half-applied. Let SQLAlchemy issue
    # BEGIN itself so schema changes roll back like everything else.
    @event.listens_for(engine, "connect")
    def _disable_pysqlite_transactions(dbapi_connection, _):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _begin(connection):
        connection.exec_driver_sql("BEGIN")

    return engine


engine = make_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
