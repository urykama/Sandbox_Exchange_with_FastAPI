# app/models/responses.py
"""
Схемы ответов биржи.

Только то, что биржа отдаёт боту.
"""

from pydantic import BaseModel


class Candle(BaseModel):
    """Одна свеча."""

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class KlinesResponse(BaseModel):
    """GET /klines — список свечей."""

    symbol: str
    candles: list[Candle]
    current_idx: int


class OrderResponse(BaseModel):
    """Ответ на POST /order и POST /cancel."""

    status: str
    side: str | None = None
    size: float | None = None
    price: float | None = None
    commission: float | None = None
    error: str | None = None


class Position(BaseModel):
    """Открытая позиция."""

    side: str
    size: float
    entry_price: float
    entry_time: int
    sl: float | None = None
    tp: float | None = None
    commission_paid: float


class PositionResponse(BaseModel):
    """GET /position — текущая позиция или None."""

    position: Position | None


class NextResponse(BaseModel):
    """POST /next — результат сдвига."""

    status: str
    current_idx: int
    total: int
    finished: bool


class ResetResponse(BaseModel):
    """POST /reset — результат сброса."""

    status: str
    balance: float
    current_idx: int


class HealthResponse(BaseModel):
    """GET /health."""

    status: str
    project: str
    version: str
    mode: str