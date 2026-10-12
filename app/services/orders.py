# app/services/orders.py — добавить
"""Проверка триггеров."""

from app.services.state import ExchangeState
from app.services.candles import get_current_candle


def check_triggers(state: ExchangeState) -> None:
    """
    Проверить ордера на срабатывание триггера.

    Условие: low <= triggerPrice <= high текущей свечи.
    """
    from app.services.positions import process_order

    candle = get_current_candle(state)
    if candle is None:
        return

    remaining = []
    for order in state.orders:
        trigger = order.get("triggerPrice")
        if trigger is None:
            remaining.append(order)
            continue

        trigger_f = float(trigger)
        if candle["low"] <= trigger_f <= candle["high"]:
            order["status"] = "Filled"
            # print(f"🎯 Триггер: {order['orderId']} {order['side']} {order['qty']} @ {trigger_f}", flush=True)
            process_order(state, order)
            state.orders.remove(order)


    state.orders = remaining