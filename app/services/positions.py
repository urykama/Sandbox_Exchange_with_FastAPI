# app/services/positions.py
"""Работа с позициями: открытие, закрытие, разворот."""

from app.services.state import ExchangeState
from app.services.balance import calc_pnl, calc_pnl_pct
from config import TRADES_PATH, ORDERS_PATH
from app.services.trades import save_all


def average_position(state: ExchangeState, order: dict) -> None:
    """Усреднение — пока не реализовано."""
    print("⚠️  Усреднение не реализовано", flush=True)



def close_position(
    state: ExchangeState,
    order: dict,
    reason: str = "manual",
) -> None:
    """
    Закрывает позицию полностью или частично.

    Учитывает reduceOnly:
    - True  → остаток ордера сгорает (order["qty"] = "0")
    - False → остаток остаётся в ордере для разворота
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

    # Остаток ордера
    if order.get("reduceOnly"):
        order["qty"] = "0"
    else:
        order["qty"] = str(order_qty - close_size)
    order["status"] = "PartiallyFilled" if float(order["qty"]) > 0 else "Filled"

    # Сохранение раз в N сделок
    if len(state.trades) % 5 == 0:
        save_all(state, TRADES_PATH, ORDERS_PATH)


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
        f"bal={state.balance:.2f}",
        end='',
    )
    return state.position
