# app/services/candles.py
"""
Работа со свечами.

Загрузка из CSV, отдача боту, движение указателя времени.
Никакой торговли — только свечи и время.
"""

import csv
from pathlib import Path

from app.services.state import ExchangeState


# ============================================================
# Загрузка
# ============================================================

def load_candles(state: ExchangeState, path: str) -> int:
    """
    Загружает свечи из CSV в state.candles.

    Ожидаемые колонки: timestamp,open,high,low,close,volume
    Возвращает количество загруженных свечей.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"CSV не найден: {file_path}")

    candles = []
    with file_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candles.append({
                "timestamp": int(row["timestamp"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            })

    state.candles = candles
    state.current_idx = 0

    return len(candles)


# ============================================================
# Чтение
# ============================================================

def get_klines(state: ExchangeState, limit: int) -> list:
    """
    Возвращает свечи до current_idx включительно.

    Это то, что "видит" бот в момент времени current_idx.
    Будущие свечи не отдаются.
    """
    end = state.current_idx + 1
    start = max(0, end - limit)
    return state.candles[start:end]


def get_current_candle(state: ExchangeState) -> dict | None:
    """Текущая свеча (на которой стоит указатель)."""
    if not state.candles:
        return None
    if state.current_idx >= len(state.candles):
        return None
    return state.candles[state.current_idx]


# ============================================================
# Движение времени
# ============================================================

def next_candle(state: ExchangeState) -> bool:
    """
    Сдвигает указатель на +1 свечу.

    Возвращает True, если сдвинулись.
    False — если свечи кончились.
    """
    if state.current_idx + 1 >= len(state.candles):
        return False

    state.current_idx += 1
    return True


def is_finished(state: ExchangeState) -> bool:
    """Все свечи пройдены?"""
    return state.current_idx >= len(state.candles) - 1


def reset_candles(state: ExchangeState) -> None:
    """Возвращает указатель в начало. Свечи не трогает."""
    state.current_idx = 0