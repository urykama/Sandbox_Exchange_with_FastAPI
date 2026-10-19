# app/services/orders.py
"""Проверка триггеров и диспетчеризация ордеров."""

from app.services.state import ExchangeState
from app.services.candles import get_current_candle
from app.services.positions import open_position, close_position, average_position


# ============================================================
# Триггеры
# ============================================================

def check_triggers(state: ExchangeState) -> None:
    """
    Проверить ордера на срабатывание триггера.
    Условие: low <= triggerPrice <= high текущей свечи.
    """
    candle = get_current_candle(state)
    if candle is None:
        return

    # Копия списка — чтобы безопасно удалять во время цикла
    for order in state.orders[:]:
        trigger = order.get("triggerPrice")
        if trigger is None:
            continue

        if candle["low"] <= float(trigger) <= candle["high"]:
            process_order(state, order)
            state.orders.remove(order)


# ============================================================
# Диспетчер
# ============================================================

def process_order(state: ExchangeState, order: dict) -> None:
    """Решает, что делать с исполненным ордером."""
    symbol = order["symbol"]
    side = "long" if order["side"] == "Buy" else "short"
    price = float(order["triggerPrice"])

    if state.position is not None:
        if state.position["side"] == side:
            average_position(state, order)  # усреднение (потом)
            return
        else:
            close_position(state, order, reason="reversal")

    if float(order["qty"]) > 0:
        open_position(state, side, float(order["qty"]), symbol, price)
        order["status"] = "Filled"