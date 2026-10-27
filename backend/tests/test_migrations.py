import pytest
from sqlalchemy import inspect, text

from app.database import Base, make_engine
from app.migrate import upgrade_db

# The trades table exactly as the MVP's create_all made it, before migrations existed.
LEGACY_SCHEMA = [
    """CREATE TABLE trades (
        id INTEGER NOT NULL, symbol VARCHAR(20) NOT NULL, side VARCHAR(5) NOT NULL,
        entry_price FLOAT NOT NULL, exit_price FLOAT, position_size FLOAT NOT NULL,
        stop_loss FLOAT, take_profit FLOAT, trade_date DATE NOT NULL, strategy VARCHAR(50),
        notes TEXT, emotion_before VARCHAR(30), emotion_after VARCHAR(30),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, PRIMARY KEY (id))""",
    "CREATE INDEX ix_trades_symbol ON trades (symbol)",
    "CREATE INDEX ix_trades_trade_date ON trades (trade_date)",
    "CREATE INDEX ix_trades_strategy ON trades (strategy)",
]


@pytest.fixture
def engine(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'journal.db'}")
    yield engine
    engine.dispose()


def columns(engine):
    return {c["name"] for c in inspect(engine).get_columns("trades")}


def test_fresh_database_matches_models(engine):
    upgrade_db(engine)
    assert columns(engine) == set(Base.metadata.tables["trades"].columns.keys())


def test_legacy_database_is_upgraded_without_losing_data(engine):
    with engine.begin() as conn:
        for stmt in LEGACY_SCHEMA:
            conn.execute(text(stmt))
        conn.execute(text(
            "INSERT INTO trades (id, symbol, side, entry_price, exit_price, position_size, trade_date, notes) "
            "VALUES (1, 'AAPL', 'long', 100, 110, 10, '2026-10-01', 'closed'),"
            "       (2, 'TSLA', 'short', 200, NULL, 1, '2026-10-03', 'open')"
        ))

    upgrade_db(engine)
    upgrade_db(engine)  # running again on every start must be a no-op

    assert columns(engine) == set(Base.metadata.tables["trades"].columns.keys())
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, entry_date, exit_date, fees, notes FROM trades ORDER BY id")).all()
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert rows == [(1, "2026-10-01", "2026-10-01", 0, "closed"), (2, "2026-10-03", None, 0, "open")]
    assert version == "0002"


def test_failed_schema_change_rolls_back(engine):
    # Python's sqlite3 would normally commit DDL immediately; make_engine must prevent that.
    with pytest.raises(RuntimeError):
        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE half_done (id INTEGER)"))
            raise RuntimeError("migration failed")
    assert not inspect(engine).has_table("half_done")
