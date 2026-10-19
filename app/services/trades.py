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

ORDERS_COLUMNS = [
    "createdAt",
    "symbol",
    "side",
    "triggerPrice",
    "qty",
    "status",
    "orderId",
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


def save_orders(state: ExchangeState, path: str) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ORDERS_COLUMNS)
        w.writeheader()
        for o in state.orders_history:
            row = {k: o.get(k, "") for k in ORDERS_COLUMNS}
            w.writerow(row)

    return len(state.orders_history)


def save_all(state: ExchangeState, trades_path: str, orders_path: str) -> None:
    n_trades = save_trades(state, trades_path)
    n_orders = save_orders(state, orders_path)
    # print(f"💾 CSV: {n_trades} сделок, {n_orders} ордеров", flush=True)