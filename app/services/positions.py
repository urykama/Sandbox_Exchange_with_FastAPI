# app/services/positions.py
"""Работа с позициями: открытие, закрытие, разворот."""

from app.services.state import ExchangeState
from app.services.balance import calc_pnl, calc_pnl_pct
from config import TRADES_PATH, ORDERS_PATH
from app.services.trades import save_all

def open_position(
    state: ExchangeState,
    side: str,
    size: float,
    symbol: str,
    price: float,
) -> dict:
    state.position = {
        "symbol": symbol,
        "side": side,
        "size": size,
        "entry_price": price,
        "entry_time": state.candles[state.current_idx]["timestamp"],
    }
    state.balance -= size * price

    print(
        f"📈 Открыта: {side:5}  {size:10.3} @ {price} | "
        f"balance={state.balance:.2f}",
        flush=True,
    )
    return state.position


def close_position(
    state: ExchangeState,
    order: dict,
    reason: str = "manual",
) -> float:
    price = float(order["triggerPrice"])
    position = state.position

    pnl = calc_pnl(position["entry_price"], price, position["size"], position["side"])
    pnl_pct = calc_pnl_pct(position["entry_price"], price, position["side"])

    state.balance += position["size"] * position["entry_price"] + pnl
    state.realized_pnl += pnl

    trade = {
        "symbol":      position["symbol"],
        "side":        position["side"],
        "entry_time":  position["entry_time"],
        "exit_time":   state.candles[state.current_idx]["timestamp"],
        "entry_price": position["entry_price"],
        "exit_price":  price,
        "size":        position["size"],
        "pnl":         round(pnl, 4),
        "pnl_pct":     round(pnl_pct, 2),
        "balance":     round(state.balance, 2),
        "reason":      reason,
    }
    state.trades.append(trade)
    state.position = None

    print(
        f"💰 {trade['exit_time']} | {position['size']:10.3} @ {price}  PnL={pnl:+.4f} | "
        f"balance={state.balance:.2f}",
        flush=True,
    )

    # Сохранение раз в N сделок
    if len(state.trades) % 20 == 0:
        save_all(state, TRADES_PATH, ORDERS_PATH)
    return float(order["qty"]) - position["size"]

def process_order(state: ExchangeState, order: dict) -> None:
    symbol = order["symbol"]
    side = "long" if order["side"] == "Buy" else "short"
    price = float(order["triggerPrice"])

    # if state.position is None:
    #     open_position(state, side, size, symbol, price)
    #     return

    # if state.position["side"] == side:
    #     print(f"⚠️  Добор не реализован", flush=True)
    #     return

    size_remainder = close_position(state, order, reason="reversal")
    if size_remainder > 0:
        open_position(state, side, size_remainder, symbol, price)