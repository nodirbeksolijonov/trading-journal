import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db, make_engine
from app.main import app


@pytest.fixture
def client():
    # Fresh in-memory database per test; StaticPool keeps one shared connection.
    engine = make_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)  # not used as a context manager, so the real DB is never created
    app.dependency_overrides.clear()


@pytest.fixture
def make_trade(client):
    def _make(**overrides):
        payload = {
            "symbol": "aapl",
            "side": "long",
            "entry_price": 100,
            "exit_price": 110,
            "position_size": 10,
            "stop_loss": 95,
            "take_profit": 115,
            "entry_date": "2026-10-01",
            "strategy": "breakout",
            "emotion_before": "calm",
            "emotion_after": "confident",
            **overrides,
        }
        # Closed trades exit the day they were entered unless a test says otherwise.
        if "exit_date" not in overrides:
            payload["exit_date"] = None if payload["exit_price"] is None else payload["entry_date"]
        res = client.post("/api/trades", json=payload)
        assert res.status_code == 201, res.text
        return res.json()

    return _make
