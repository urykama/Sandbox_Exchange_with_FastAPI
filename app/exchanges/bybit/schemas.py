# app/exchanges/bybit/schemas.py
"""Схемы Bybit: запрос и ответ /v5/order/create."""

from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    """Тело запроса Bybit /v5/order/create. Принимаем всё, что шлёт бот."""

    category: str
    symbol: str
    side: str                      # "Buy" / "Sell"
    orderType: str                 # "Market" / "Limit"
    qty: str                       # строка, как у Bybit
    price: str | None = None
    triggerPrice: str | None = None
    triggerBy: str | None = None
    triggerDirection: int | None = None
    reduceOnly: bool | None = None
    timeInForce: str | None = None
    orderLinkId: str | None = None


class OrderResult(BaseModel):
    orderId: str
    orderLinkId: str = ""


class OrderCreateResponse(BaseModel):
    """Ответ Bybit."""

    retCode: int
    retMsg: str
    result: OrderResult
    retExtInfo: dict = Field(default_factory=dict)
    time: int

# CancelAll     CancelAll       CancelAll

class OrderCancelAllRequest(BaseModel):
    """POST /v5/order/cancel-all — тело."""

    category: str
    symbol: str | None = None
    baseCoin: str | None = None
    settleCoin: str | None = None
    orderFilter: str | None = None


class CancelledOrder(BaseModel):
    orderId: str
    orderLinkId: str = ""


class CancelAllResult(BaseModel):
    list: list[CancelledOrder]


class CancelAllResponse(BaseModel):
    retCode: int
    retMsg: str
    result: CancelAllResult
    retExtInfo: dict = Field(default_factory=dict)
    time: int

# === Cancel one ===

class OrderCancelRequest(BaseModel):
    """POST /v5/order/cancel — тело."""

    category: str
    symbol: str
    orderId: str | None = None
    orderLinkId: str | None = None


class CancelResult(BaseModel):
    orderId: str
    orderLinkId: str = ""


class CancelResponse(BaseModel):
    retCode: int
    retMsg: str
    result: CancelResult
    retExtInfo: dict = Field(default_factory=dict)
    time: int


# === Market time ===
class MarketTimeResult(BaseModel):
    timeSecond: str
    timeNano: str


class MarketTimeResponse(BaseModel):
    retCode: int
    retMsg: str
    result: MarketTimeResult
    retExtInfo: dict = Field(default_factory=dict)
    time: int


# === Kline ===
class KlineResult(BaseModel):
    symbol: str
    category: str
    list: list[list[str]]


class KlineResponse(BaseModel):
    retCode: int
    retMsg: str
    result: KlineResult
    retExtInfo: dict = Field(default_factory=dict)
    time: int


# === Position list ===
class PositionInfo(BaseModel):
    symbol: str
    side: str
    size: str
    avgPrice: str
    positionValue: str
    unrealisedPnl: str
    createdTime: str
    updatedTime: str


class PositionListResult(BaseModel):
    category: str
    list: list[PositionInfo]


class PositionListResponse(BaseModel):
    retCode: int
    retMsg: str
    result: PositionListResult
    retExtInfo: dict = Field(default_factory=dict)
    time: int