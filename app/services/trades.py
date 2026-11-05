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

POSITIONS_COLUMNS = [
    "time",
    "symbol",
    "side",
    "size",
    "entry_price",
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


def save_positions(state: ExchangeState, path: str) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=POSITIONS_COLUMNS)
        w.writeheader()
        for row in state.position_history:
            w.writerow(row)

    return len(state.position_history)


def save_all(state: ExchangeState, trades_path: str, orders_path: str, positions_path: str) -> None:
    save_trades(state, trades_path)
    save_orders(state, orders_path)
    save_positions(state, positions_path)  # ← ДОБАВИТЬ
    # print(f"💾 CSV: {n_trades} сделок, {n_orders} ордеров", flush=True)


def print_statistics(state: ExchangeState) -> None:
    """Выводит красивую статистику по завершении."""
    if not state.trades:
        print("📊 Нет закрытых сделок для статистики.")
        return

    trades = state.trades

    # 1. Основные цифры
    total_pnl = sum(t['pnl'] for t in trades)
    initial = state.initial_balance
    final = state.balance
    pnl_pct = (total_pnl / initial) * 100 if initial else 0

    # 2. Win Rate
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    win_rate = (len(wins) / len(trades)) * 100 if trades else 0

    # 3. Profit Factor
    gross_profit = sum(t['pnl'] for t in wins)
    gross_loss = abs(sum(t['pnl'] for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    # 4. Средние
    avg_win = gross_profit / len(wins) if wins else 0
    avg_loss = gross_loss / len(losses) if losses else 0

    # 5. Max Drawdown (по балансу)
    balances = [initial] + [t['balance'] for t in trades]
    max_dd = 0
    peak = balances[0]
    for b in balances:
        if b > peak:
            peak = b
        dd = (peak - b) / peak * 100 if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd

    # --- Вывод ---
    print("\n" + "=" * 50)
    print(" 📊 СТАТИСТИКА ТЕСТ-БИРЖИ")
    print("=" * 50)
    print(f" 💰 Начальный баланс: {initial:.2f} USDT")
    print(f" 💰 Финальный баланс: {final:.2f} USDT")
    print(f" 📈 Общий PnL:        {total_pnl:+.2f} USDT ({pnl_pct:+.2f}%)")
    print("-" * 50)
    print(f" 📉 Всего сделок:     {len(trades)}")
    print(f" 🟢 Прибыльных:       {len(wins)} ({win_rate:.1f}%)")
    print(f" 🔴 Убыточных:        {len(losses)} ({100 - win_rate:.1f}%)")
    print("-" * 50)
    print(f" ⚖️  Profit Factor:   {profit_factor:.2f}")
    print(f" 🟢 Средняя прибыль:  {avg_win:+.2f} USDT")
    print(f" 🔴 Средний убыток:   {avg_loss:.2f} USDT")
    print(f" 📉 Max Drawdown:     {max_dd:.2f}%")
    print("=" * 50 + "\n", flush=True)