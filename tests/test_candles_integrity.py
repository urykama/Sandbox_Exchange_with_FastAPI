# tests/test_candles_integrity.py
"""
Проверка целостности CSV со свечами.

Не про биржу — про сами данные.
Пропускается, если файла нет.
"""

import csv
from pathlib import Path

import pytest

from config import CANDLES_PATH, TIMEFRAME


TIMEFRAME_MS = {
    "1m": 60_000,
    "5m": 300_000,
    "15m": 900_000,
    "1h": 3_600_000,
    "4h": 14_400_000,
    "1d": 86_400_000,
}


@pytest.fixture(scope="module")
def candles():
    """Читает CSV один раз на весь модуль. Скипает, если файла нет."""
    path = Path(CANDLES_PATH)
    if not path.exists():
        pytest.skip(f"CSV не найден: {path}")

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            {
                "timestamp": int(r["timestamp"]),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["volume"]),
            }
            for r in reader
        ]
    return rows


def test_not_empty(candles):
    assert len(candles) > 0


def test_sorted_ascending(candles):
    """Свечи от старых к новым."""
    timestamps = [c["timestamp"] for c in candles]
    assert timestamps == sorted(timestamps)


def test_no_duplicates(candles):
    """Нет повторов timestamp."""
    timestamps = [c["timestamp"] for c in candles]
    assert len(timestamps) == len(set(timestamps))


def test_no_gaps(candles):
    """Нет пропусков — шаг ровно TIMEFRAME."""
    step = TIMEFRAME_MS[TIMEFRAME]
    for prev, curr in zip(candles, candles[1:]):
        delta = curr["timestamp"] - prev["timestamp"]
        assert delta == step, (
            f"Пропуск: {prev['timestamp']} → {curr['timestamp']} "
            f"(шаг {delta}, ожидался {step})"
        )


def test_ohlc_valid(candles):
    """Базовая проверка OHLC: high >= max(open,close), low <= min(open,close)."""
    for c in candles:
        assert c["high"] >= c["open"], f"high < open: {c}"
        assert c["high"] >= c["close"], f"high < close: {c}"
        assert c["low"] <= c["open"], f"low > open: {c}"
        assert c["low"] <= c["close"], f"low > close: {c}"


def test_positive_values(candles):
    """Все цены и объём положительные."""
    for c in candles:
        assert c["open"] > 0
        assert c["high"] > 0
        assert c["low"] > 0
        assert c["close"] > 0
        assert c["volume"] >= 0