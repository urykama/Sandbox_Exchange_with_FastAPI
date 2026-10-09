# app/services/trades.py
"""
Запись результатов в CSV.

Два файла:
- trades.csv  — все закрытые сделки
- equity.csv  — баланс по свечам
"""

import csv
from pathlib import Path

from app.services.state import ExchangeState


TRADES_COLUMNS = [
    "entry_time",
    "exit_time",
    "side",
    "size_usdt",
    "entry_price",
    "exit_price",
    "pnl",
    "pnl_pct",
    "commission",
    "reason",
]

EQUITY_COLUMNS = [
    "timestamp",
    "balance",
    "realized_pnl",
]


# ============================================================
# Сделки
# ============================================================

def save_trades(state: ExchangeState, path: str) -> int:
    """Сохраняет все закрытые сделки в CSV. Возвращает количество строк."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRADES_COLUMNS)
        writer.writeheader()
        for trade in state.trades:
            writer.writerow(trade)

    return len(state.trades)


# ============================================================
# Equity
# ============================================================

def record_equity(state: ExchangeState) -> None:
    """
    Записывает текущий баланс в equity_curve.

    Вызывается на каждой новой свече.
    """
    from app.services.candles import get_current_candle

    candle = get_current_candle(state)
    if candle is None:
        return

    state.equity_curve.append({
        "timestamp": candle["timestamp"],
        "balance": round(state.balance, 4),
        "realized_pnl": round(state.realized_pnl, 4),
    })


def save_equity(state: ExchangeState, path: str) -> int:
    """Сохраняет equity-кривую в CSV. Возвращает количество строк."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EQUITY_COLUMNS)
        writer.writeheader()
        for row in state.equity_curve:
            writer.writerow(row)

    return len(state.equity_curve)


# ============================================================
# Общее
# ============================================================

def save_all(state: ExchangeState, trades_path: str, equity_path: str) -> dict:
    """Сохраняет оба файла. Возвращает счётчики."""
    return {
        "trades": save_trades(state, trades_path),
        "equity": save_equity(state, equity_path),
    }