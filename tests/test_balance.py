# tests/test_balance.py
"""Тесты математики: комиссии, PnL, проверки."""

from app.services.balance import (
    calc_commission,
    calc_order_cost,
    calc_total_cost,
    calc_pnl,
    calc_pnl_pct,
    can_afford,
)


def test_commission():
    assert calc_commission(100.0, 1.0, 0.001) == 0.1


def test_order_cost():
    assert calc_order_cost(100.0, 2.0) == 200.0


def test_total_cost():
    assert round(calc_total_cost(100.0, 1.0, 0.001), 4) == 100.1


def test_pnl_long_profit():
    assert calc_pnl(100.0, 110.0, 1.0, "long") == 10.0


def test_pnl_long_loss():
    assert calc_pnl(100.0, 90.0, 1.0, "long") == -10.0


def test_pnl_short_profit():
    assert calc_pnl(100.0, 90.0, 1.0, "short") == 10.0


def test_pnl_short_loss():
    assert calc_pnl(100.0, 110.0, 1.0, "short") == -10.0


def test_pnl_pct_long():
    assert calc_pnl_pct(100.0, 110.0, "long") == 10.0


def test_pnl_pct_short():
    assert calc_pnl_pct(100.0, 90.0, "short") == 10.0


def test_can_afford_yes():
    assert can_afford(10_000.0, 100.0, 1.0, 0.001) is True


def test_can_afford_no():
    assert can_afford(50.0, 100.0, 1.0, 0.001) is False