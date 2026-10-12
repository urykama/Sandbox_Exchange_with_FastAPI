# app/services/trades.py
"""Сохранение сделок в CSV."""

import csv
from pathlib import Path

from app.services.state import ExchangeState


TRADES_COLUMNS = [
    "symbol",
    "side",
    "entry_time",
    "exit_time",
    "entry_price",
    "exit_price",
    "size",
    "pnl",
    "pnl_pct",
    "balance",
    "reason",
]

SAVE_EVERY = 20


def save_trades(state: ExchangeState, path: str) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=TRADES_COLUMNS)
        w.writeheader()
        for t in state.trades:
            w.writerow(t)

    return len(state.trades)


def maybe_save(state: ExchangeState, path: str) -> None:
    n = len(state.trades)
    if n > 0 and n % SAVE_EVERY == 0:
        cnt = save_trades(state, path)
        print(f"💾 CSV: {cnt} сделок → {path}", flush=True)