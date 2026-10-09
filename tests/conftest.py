# tests/conftest.py
"""
Общие фикстуры для тестов.

Свечи, состояние, TestClient — всё, что нужно каждому тесту.
"""

import pytest

from app.services.state import ExchangeState


# ============================================================
# Свечи для тестов (3 штуки, детерминированные)
# ============================================================

@pytest.fixture
def sample_candles() -> list[dict]:
    return [
        {"timestamp": 1000, "open": 100.0, "high": 110.0, "low": 90.0,  "close": 105.0, "volume": 10.0},
        {"timestamp": 2000, "open": 105.0, "high": 120.0, "low": 100.0, "close": 115.0, "volume": 12.0},
        {"timestamp": 3000, "open": 115.0, "high": 125.0, "low": 95.0,  "close": 100.0, "volume": 15.0},
    ]


@pytest.fixture
def state(sample_candles) -> ExchangeState:
    """Состояние с уже загруженными свечами."""
    s = ExchangeState(initial_balance=10_000.0, symbol="BTCUSDT")
    s.candles = sample_candles
    s.current_idx = 0
    return s