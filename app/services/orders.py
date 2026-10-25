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

    # Копия списка — чтобы безопасно удалять во время цикла
    for order in state.orders[:]:
        trigger = order.get("triggerPrice")
        if trigger is None:
            continue

        if candle["low"] <= float(trigger) <= candle["high"]:

            print(f"🎯 Триггер: {order['side']:5} {order['qty']:8} @ {trigger:8}", flush=True)
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
            print(state)
            print(order)
            average_position(state, order)  # усреднение (потом)
            return
        else:
            close_position(state, order, reason="reversal")

    if float(order["qty"]) > 0:
        open_position(state, side, float(order["qty"]), symbol, price)


def check_limit_orders(state: ExchangeState) -> None:
    """
    Проверяет лимитные ордера на исполнение.
    Buy  исполняется, если low <= price.
    Sell исполняется, если high >= price.
    """
    candle = get_current_candle(state)


    for order in state.orders[:]:  # копия списка для безопасного удаления
        # Пропускаем всё, что не Limit, и всё, у чего есть триггер
        if order["orderType"] != "Limit" or order.get("triggerPrice") is not None:
            continue

        price = float(order["price"])
        qty = float(order["qty"])
        side = order["side"]
        executed = False

        if side == "Buy" and candle["low"] <= price:
            executed = True
        elif side == "Sell" and candle["high"] >= price:
            executed = True

        if executed:
            # Для process_order цена исполнения должна лежать в triggerPrice
            order["triggerPrice"] = str(price)
            order["status"] = "Filled"
            print(f"🎯 Лимит  : {side:5} {order['qty']:8} @ {price:8.6g}", flush=True)
            process_order(state, order)
            state.orders.remove(order)