# tests/test_trades.py
"""Тесты записи CSV."""

import csv
from pathlib import Path

from app.services.orders import open_position, close_position
from app.services.candles import next_candle
from app.services.trades import save_trades, save_equity, record_equity


def test_save_trades(tmp_path, state):
    open_position(state, "long", 1.0, 0.001)
    next_candle(state)
    close_position(state, 0.001)

    path = tmp_path / "trades.csv"
    n = save_trades(state, str(path))
    assert n == 1

    with path.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["side"] == "long"
    assert "pnl" in rows[0]


def test_save_equity(tmp_path, state):
    record_equity(state)
    next_candle(state)
    record_equity(state)

    path = tmp_path / "equity.csv"
    n = save_equity(state, str(path))
    assert n == 2