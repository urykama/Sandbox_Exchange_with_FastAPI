# app/services/balance.py
"""
Деньги: PnL, комиссии, проверки.

Чистые функции. Не знают про state, не знают про HTTP.
Принимают числа — возвращают числа.
"""


# ============================================================
# Комиссии
# ============================================================

def calc_commission(price: float, size: float, commission_pct: float) -> float:
    """Комиссия со сделки: цена × объём × процент."""
    return price * size * commission_pct


# ============================================================
# Стоимость
# ============================================================

def calc_order_cost(price: float, size: float) -> float:
    """Стоимость ордера: цена × объём."""
    return price * size


def calc_total_cost(price: float, size: float, commission_pct: float) -> float:
    """Стоимость + комиссия. Столько нужно иметь на балансе."""
    return calc_order_cost(price, size) + calc_commission(price, size, commission_pct)


# ============================================================
# PnL
# ============================================================

def calc_pnl(entry_price: float, exit_price: float, size: float, side: str) -> float:
    """
    PnL по закрытой сделке.

    side: "long" или "short"
    long:  (exit - entry) * size
    short: (entry - exit) * size
    """
    if side == "long":
        return (exit_price - entry_price) * size
    elif side == "short":
        return (entry_price - exit_price) * size
    else:
        raise ValueError(f"Неизвестная сторона: {side}")


def calc_pnl_pct(entry_price: float, exit_price: float, side: str) -> float:
    """PnL в процентах от цены входа."""
    if side == "long":
        return (exit_price - entry_price) / entry_price * 100
    elif side == "short":
        return (entry_price - exit_price) / entry_price * 100
    else:
        raise ValueError(f"Неизвестная сторона: {side}")


# ============================================================
# Проверки
# ============================================================

def can_afford(balance: float, price: float, size: float, commission_pct: float) -> bool:
    """Хватает ли денег на ордер (с учётом комиссии)."""
    return balance >= calc_total_cost(price, size, commission_pct)