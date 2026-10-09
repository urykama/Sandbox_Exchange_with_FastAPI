# app/services/orders.py
"""
Исполнение ордеров.

Market — сразу по close текущей свечи.
SL/TP — проверяются по high/low каждой новой свечи.
"""

from app.services.state import ExchangeState
from app.services.candles import get_current_candle
from app.services.balance import (
    calc_commission,
    calc_total_cost,
    calc_pnl,
    calc_pnl_pct,
    can_afford,
)


# ============================================================
# Открытие позиции
# ============================================================

def open_position(
    state: ExchangeState,
    side: str,
    size: float,
    commission_pct: float,
    price: float | None = None,
    sl: float | None = None,
    tp: float | None = None,
) -> dict:
    """
    Открывает позицию по market.

    side: "long" или "short"
    size: объём в базовой валюте
    price: если None — берётся close текущей свечи
    """
    if state.position is not None:
        return {"error": "position already open"}

    candle = get_current_candle(state)
    if candle is None:
        return {"error": "no candles"}

    fill_price = price if price is not None else candle["close"]

    if not can_afford(state.balance, fill_price, size, commission_pct):
        return {"error": "insufficient balance"}

    commission = calc_commission(fill_price, size, commission_pct)
    cost = calc_total_cost(fill_price, size, commission_pct)

    state.balance -= cost
    state.position = {
        "side": side,
        "size": size,
        "entry_price": fill_price,
        "entry_time": candle["timestamp"],
        "sl": sl,
        "tp": tp,
        "commission_paid": commission,
    }

    return {
        "status": "filled",
        "side": side,
        "size": size,
        "price": fill_price,
        "commission": commission,
    }


# ============================================================
# Закрытие позиции
# ============================================================

def close_position(
    state: ExchangeState,
    commission_pct: float,
    price: float | None = None,
    reason: str = "manual",
) -> dict:
    """
    Закрывает текущую позицию.

    price: если None — берётся close текущей свечи
    reason: "manual" / "sl" / "tp" / "end"
    """
    if state.position is None:
        return {"error": "no position"}

    candle = get_current_candle(state)
    if candle is None:
        return {"error": "no candles"}

    exit_price = price if price is not None else candle["close"]
    pos = state.position

    pnl = calc_pnl(pos["entry_price"], exit_price, pos["size"], pos["side"])
    pnl_pct = calc_pnl_pct(pos["entry_price"], exit_price, pos["side"])
    commission = calc_commission(exit_price, pos["size"], commission_pct)
    total_commission = commission + pos["commission_paid"]

    # Возвращаем стоимость позиции + PnL - комиссия
    entry_cost = pos["entry_price"] * pos["size"]
    state.balance += entry_cost + pnl - commission
    state.realized_pnl += pnl - total_commission

    trade = {
        "entry_time":  pos["entry_time"],
        "exit_time":   candle["timestamp"],
        "side":        pos["side"],
        "size_usdt":   round(pos["size"] * pos["entry_price"], 2),
        "entry_price": pos["entry_price"],
        "exit_price":  exit_price,
        "pnl":         round(pnl - total_commission, 4),
        "pnl_pct":     round(pnl_pct, 2),
        "commission":  round(total_commission, 4),
        "reason":      reason,
    }
    state.trades.append(trade)
    state.position = None

    return {"status": "closed", **trade}


# ============================================================
# Проверка SL/TP на новой свече
# ============================================================

def check_sl_tp(state: ExchangeState, commission_pct: float) -> dict | None:
    """
    Проверяет SL/TP на текущей свече.

    Если сработал — закрывает позицию.
    Возвращает результат закрытия или None.
    """
    if state.position is None:
        return None

    candle = get_current_candle(state)
    if candle is None:
        return None

    pos = state.position
    sl = pos.get("sl")
    tp = pos.get("tp")

    if pos["side"] == "long":
        if sl is not None and candle["low"] <= sl:
            return close_position(state, commission_pct, price=sl, reason="sl")
        if tp is not None and candle["high"] >= tp:
            return close_position(state, commission_pct, price=tp, reason="tp")
    else:  # short
        if sl is not None and candle["high"] >= sl:
            return close_position(state, commission_pct, price=sl, reason="sl")
        if tp is not None and candle["low"] <= tp:
            return close_position(state, commission_pct, price=tp, reason="tp")

    return None