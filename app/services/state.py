# app/services/state.py
"""Состояние биржи."""

from dataclasses import dataclass, field


@dataclass
class ExchangeState:
    """Состояние тест-биржи."""

    initial_balance: float = 10_000.0
    balance: float = 10_000.0
    realized_pnl: float = 0.0

    symbol: str = "BTCUSDT"
    position: dict | None = None
    orders: list = field(default_factory=list)

    candles: list = field(default_factory=list)
    current_idx: int = 0

    trades: list = field(default_factory=list)
    equity_curve: list = field(default_factory=list)

    def reset(self) -> None:
        self.balance = self.initial_balance
        self.realized_pnl = 0.0
        self.position = None
        self.orders = []
        self.current_idx = 0
        self.trades = []
        self.equity_curve = []

    def __repr__(self) -> str:
        return (
            f"ExchangeState("
            f"balance={self.balance:.2f}, "
            f"pnl={self.realized_pnl:.2f}, "
            f"idx={self.current_idx}/{len(self.candles)}, "
            f"position={'yes' if self.position else 'no'})"
        )