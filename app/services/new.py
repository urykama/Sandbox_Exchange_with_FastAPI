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
    """
    Закрывает позицию (полностью или частично).

    Возвращает остаток объёма ордера.
    0 — ордер весь ушёл в закрытие.
    >0 — остаток, на который открыть встречную позицию.
    """
    price = float(order["triggerPrice"])
    order_qty = float(order["qty"])
    position = state.position

    pos_size = position["size"]
    close_size = min(order_qty, pos_size)

    # PnL на закрываемую часть
    pnl = calc_pnl(position["entry_price"], price, close_size, position["side"])
    pnl_pct = calc_pnl_pct(position["entry_price"], price, position["side"])

    # Баланс
    state.balance += close_size * position["entry_price"] + pnl
    state.realized_pnl += pnl

    trade = {
        "symbol":      position["symbol"],
        "side":        position["side"],
        "entry_time":  position["entry_time"],
        "exit_time":   state.candles[state.current_idx]["timestamp"],
        "entry_price": position["entry_price"],
        "exit_price":  price,
        "size":        close_size,
        "pnl":         round(pnl, 4),
        "pnl_pct":     round(pnl_pct, 2),
        "balance":     round(state.balance, 2),
        "reason":      reason,
    }
    state.trades.append(trade)

    print(
        f"💰 {trade['exit_time']} | {close_size:10.3} @ {price}  "
        f"PnL={pnl:+.4f} | balance={state.balance:.2f}",
        flush=True,
    )

    # Обновить позицию
    if close_size >= pos_size:
        state.position = None
    else:
        state.position["size"] = pos_size - close_size
    # Сохранение раз в N сделок
    if len(state.trades) % 20 == 0:
        save_all(state, TRADES_PATH, ORDERS_PATH)
    return order_qty - close_size

def process_order(state: ExchangeState, order: dict) -> None:
    symbol = order["symbol"]
    side = "long" if order["side"] == "Buy" else "short"
    price = float(order["triggerPrice"])

    if state.position is not None:
        # close position наверное сам должен разобраться
        # закрывать
        # закрывать частично
        # или увеличить позицию ( усреднение)
        # order["qty"] - должен поменяться в close_position
        close_position(state, order, reason="reversal")

    if float(order["qty"]) > 0:
        open_position(state, side, float(order["qty"]), symbol, price)