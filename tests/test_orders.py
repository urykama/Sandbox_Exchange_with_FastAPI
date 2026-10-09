# tests/test_orders.py
"""Тесты исполнения ордеров."""

from app.services.orders import open_position, close_position, check_sl_tp
from app.services.candles import next_candle


COMMISSION = 0.001


def test_open_long(state):
    result = open_position(state, "long", 1.0, COMMISSION)
    assert result["status"] == "filled"
    assert state.position is not None
    assert state.position["side"] == "long"
    assert state.position["entry_price"] == 105.0


def test_open_rejects_if_position_exists(state):
    open_position(state, "long", 1.0, COMMISSION)
    result = open_position(state, "long", 1.0, COMMISSION)
    assert "error" in result


def test_open_rejects_if_no_money(state):
    state.balance = 1.0
    result = open_position(state, "long", 1.0, COMMISSION)
    assert "error" in result


def test_balance_decreases_on_open(state):
    before = state.balance
    open_position(state, "long", 1.0, COMMISSION)
    assert state.balance < before


def test_close_long_profit(state):
    open_position(state, "long", 1.0, COMMISSION)   # entry 105
    next_candle(state)                                # close 115
    result = close_position(state, COMMISSION)
    assert result["status"] == "closed"
    assert result["pnl"] > 0
    assert state.position is None
    assert len(state.trades) == 1


def test_close_without_position(state):
    result = close_position(state, COMMISSION)
    assert "error" in result


def test_sl_triggers_on_low(state):
    """Long, SL=95, свеча 2 low=100 — не сработал."""
    open_position(state, "long", 1.0, COMMISSION, sl=95.0)
    next_candle(state)
    result = check_sl_tp(state, COMMISSION)
    assert result is None


def test_sl_triggers(state):
    """Long, SL=100, свеча 3 low=95 — сработал."""
    open_position(state, "long", 1.0, COMMISSION, sl=100.0)
    next_candle(state)
    next_candle(state)
    result = check_sl_tp(state, COMMISSION)
    assert result is not None
    assert result["reason"] == "sl"


def test_tp_triggers(state):
    """Long, TP=120, свеча 2 high=120 — сработал."""
    open_position(state, "long", 1.0, COMMISSION, tp=120.0)
    next_candle(state)
    result = check_sl_tp(state, COMMISSION)
    assert result is not None
    assert result["reason"] == "tp"


def test_short_tp_triggers(state):
    """Short, TP=100, свеча 3 low=95 — сработал."""
    open_position(state, "short", 1.0, COMMISSION, tp=100.0)
    next_candle(state)
    next_candle(state)
    result = check_sl_tp(state, COMMISSION)
    assert result is not None
    assert result["reason"] == "tp"