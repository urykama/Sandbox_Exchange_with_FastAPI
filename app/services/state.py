# app/services/state.py
"""
Состояние биржи.

Единственный объект, который хранит всё, что биржа "помнит":
баланс, позицию, ордера, свечи, указатель времени.

Никакой логики — только хранение и сброс.
"""

from dataclasses import dataclass, field


@dataclass
class ExchangeState:
    """Состояние тест-биржи."""

    # === Деньги ===
    initial_balance: float = 10_000.0
    balance: float = 10_000.0
    realized_pnl: float = 0.0

    # === Торговля ===
    symbol: str = "BTCUSDT"
    position: dict | None = None
    orders: list = field(default_factory=list)

    # === Данные ===
    candles: list = field(default_factory=list)
    current_idx: int = 0

    # === История (для CSV) ===
    trades: list = field(default_factory=list)
    equity_curve: list = field(default_factory=list)

    def reset(self) -> None:
        """Сброс к начальному состоянию."""
        self.balance = self.initial_balance
        self.realized_pnl = 0.0
        self.position = None
        self.orders = []
        self.current_idx = 0
        self.trades = []
        self.equity_curve = []
        # candles НЕ трогаем — они загружены один раз

    def to_dict(self) -> dict:
        """Состояние как словарь (для API)."""
        return {
            "symbol": self.symbol,
            "balance": self.balance,
            "realized_pnl": self.realized_pnl,
            "position": self.position,
            "orders_count": len(self.orders),
            "current_idx": self.current_idx,
            "candles_total": len(self.candles),
        }

    def __repr__(self) -> str:
        return (
            f"ExchangeState("
            f"balance={self.balance:.2f}, "
            f"pnl={self.realized_pnl:.2f}, "
            f"idx={self.current_idx}/{len(self.candles)}, "
            f"position={'yes' if self.position else 'no'})"
        )