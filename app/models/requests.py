# app/models/requests.py
"""
Схемы запросов от бота.

Только то, что бот присылает бирже.
"""

from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    """POST /order — выставить ордер."""

    side: str = Field(..., description="long или short")
    size: float = Field(..., gt=0, description="объём в базовой валюте")
    type: str = Field("market", description="market (пока только market)")
    price: float | None = Field(None, description="для limit, пока не используется")
    sl: float | None = Field(None, description="stop-loss")
    tp: float | None = Field(None, description="take-profit")


class NextRequest(BaseModel):
    """POST /next — сдвинуть свечу. Может быть пустым."""

    count: int = Field(1, ge=1, description="на сколько свечей сдвинуть")


class ResetRequest(BaseModel):
    """POST /reset — сброс. Может быть пустым."""

    reload_candles: bool = Field(False, description="перезагрузить ли CSV")