# tests/test_candles.py
"""Тесты работы со свечами и временем."""

import pytest

from app.services.candles import (
    get_klines,
    get_current_candle,
    next_candle,
    is_finished,
    reset_candles,
)


def test_get_current_candle(state):
    c = get_current_candle(state)
    assert c["timestamp"] == 1000


def test_get_klines_initial(state):
    """На старте видна только первая свеча."""
    candles = get_klines(state, limit=100)
    assert len(candles) == 1
    assert candles[0]["timestamp"] == 1000


def test_next_moves_index(state):
    assert next_candle(state) is True
    assert state.current_idx == 1


def test_get_klines_after_next(state):
    next_candle(state)
    candles = get_klines(state, limit=100)
    assert len(candles) == 2


def test_next_stops_at_end(state):
    next_candle(state)
    next_candle(state)
    assert next_candle(state) is False
    assert state.current_idx == 2


def test_is_finished(state):
    assert is_finished(state) is False
    next_candle(state)
    next_candle(state)
    assert is_finished(state) is True


def test_reset_candles(state):
    next_candle(state)
    next_candle(state)
    reset_candles(state)
    assert state.current_idx == 0