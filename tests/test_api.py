# tests/test_api.py

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_state
from app.services.state import ExchangeState


def _make_state() -> ExchangeState:
    s = ExchangeState(initial_balance=10_000.0, symbol="TESTUSDT")
    s.candles = [
        {"timestamp": 1000, "open": 100.0, "high": 110.0, "low": 90.0,  "close": 105.0, "volume": 10.0},
        {"timestamp": 2000, "open": 105.0, "high": 120.0, "low": 100.0, "close": 115.0, "volume": 12.0},
    ]
    return s


@pytest.fixture
def client():
    """Свежий state + TestClient на каждый тест."""
    state = _make_state()
    app.dependency_overrides[get_state] = lambda: state
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_klines(client):
    r = client.get("/klines?limit=10")
    assert r.status_code == 200
    assert len(r.json()["candles"]) == 1


def test_open_position(client):
    r = client.post("/order", json={"side": "long", "size": 1.0})
    assert r.status_code == 200
    assert r.json()["status"] == "filled"


def test_position(client):
    # Сначала открыть — потом проверить
    client.post("/order", json={"side": "long", "size": 1.0})
    r = client.get("/position")
    assert r.status_code == 200
    assert r.json()["position"] is not None


def test_next(client):
    r = client.post("/next", json={"count": 1})
    assert r.status_code == 200
    assert r.json()["current_idx"] == 1


def test_reset(client):
    r = client.post("/reset", json={})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"