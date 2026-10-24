# app/exchanges/bybit/router.py
"""Bybit-совместимые эндпоинты."""

import time
import uuid

from fastapi import APIRouter, Header, Request, Depends

from app.core.dependencies import get_state
from app.services.state import ExchangeState
from app.exchanges.bybit.schemas import (
    OrderCreateRequest,
    OrderCreateResponse,
    OrderResult,
    OrderCancelAllRequest,
    CancelAllResponse,
    CancelAllResult,
    CancelledOrder,
    CancelResponse,
    OrderCancelRequest,
    CancelResult,
    MarketTimeResponse,
    MarketTimeResult,
    KlineResponse,
    KlineResult,
    PositionListResponse,
    PositionListResult,
    PositionInfo,
)
from app.services.orders import check_triggers

router = APIRouter(prefix="/v5", tags=["bybit"])


@router.get("/order/list")
def order_list(state: ExchangeState = Depends(get_state)) -> dict:
    """Показать все принятые ордера (не по стандарту Bybit — для отладки)."""
    return {
        "count": len(state.orders),
        "orders": state.orders,
    }


@router.post("/order/cancel-all", response_model=CancelAllResponse)
async def order_cancel_all(
    request: Request,
    state: ExchangeState = Depends(get_state),
) -> CancelAllResponse:
    """Отменить все ордера (по символу или все)."""
    body = await request.json()

    # print("\n" + "=" * 60)
    # print("📥 POST /v5/order/cancel-all")
    # print(f"   BODY: {body}")
    # print("=" * 60, flush=True)

    req = OrderCancelAllRequest(**body)

    # Отбираем, что отменять
    cancelled = []
    for order in state.orders:
        match = True
        if req.symbol is not None and order["symbol"] != req.symbol:
            match = False
        if req.category is not None and order["category"] != req.category:
            match = False

        if match:
            order["status"] = "Cancelled"  # ← добавить
            cancelled.append({
                "orderId": order["orderId"],
                "orderLinkId": order["orderLinkId"],
            })
            state.orders.remove(order)

    # print(f"📤 Отменено: {len(cancelled)}, осталось: {len(state.orders)}")
    # print("=" * 60 + "\n", flush=True)

    return CancelAllResponse(
        retCode=0,
        retMsg="OK",
        result=CancelAllResult(list=[CancelledOrder(**c) for c in cancelled]),
        retExtInfo={},
        time=int(time.time() * 1000),
    )

@router.post("/order/cancel", response_model=CancelResponse)
async def order_cancel(
    request: Request,
    state: ExchangeState = Depends(get_state),
) -> CancelResponse:
    body = await request.json()
    req = OrderCancelRequest(**body)

    target = None
    for order in state.orders:
        if req.orderId and order["orderId"] == req.orderId:
            target = order
            break
        if req.orderLinkId and order["orderLinkId"] == req.orderLinkId:
            target = order
            break

    # Если не нашли — Bybit возвращает ошибку 110001
    if target is None:
        return CancelResponse(
            retCode=110001,
            retMsg="Order does not exist.",
            result=CancelResult(orderId=req.orderId or "", orderLinkId=req.orderLinkId or ""),
            retExtInfo={},
            time=int(time.time() * 1000),
        )

    target["status"] = "Cancelled"
    state.orders.remove(target)

    # print(f"🗑️  Отменён: {target['orderId']}", flush=True)

    return CancelResponse(
        retCode=0,
        retMsg="OK",
        result=CancelResult(
            orderId=target["orderId"],
            orderLinkId=target["orderLinkId"],
        ),
        retExtInfo={},
        time=int(time.time() * 1000),
    )


# ============================================================
# Market time
# ============================================================

@router.get("/market/time", response_model=MarketTimeResponse)
def market_time(state: ExchangeState = Depends(get_state)) -> MarketTimeResponse:
    now_ms = state.candles[state.current_idx]["timestamp"]
    now_s = now_ms // 1000
    now_ns = now_ms * 1_000_000

    return MarketTimeResponse(
        retCode=0,
        retMsg="OK",
        result=MarketTimeResult(
            timeSecond=str(now_s),
            timeNano=str(now_ns),
        ),
        retExtInfo={},
        time=now_ms,
    )


# ============================================================
# Position list
# ============================================================

@router.get("/position/list", response_model=PositionListResponse)
def position_list(
    category: str,
    symbol: str | None = None,
    state: ExchangeState = Depends(get_state),
) -> PositionListResponse:
    """Текущая позиция (если есть)."""

    # Двигаем время
    state.current_idx += 1

    # Проверка триггеров
    check_triggers(state)


    positions = []

    if state.position is not None:
        pos = state.position
        # Маппинг: long/short → Buy/Sell
        bybit_side = "Buy" if pos["side"] == "long" else "Sell"

        positions.append(PositionInfo(
            symbol=state.symbol,
            side=bybit_side,
            size=str(pos["size"]),
            avgPrice=str(pos["entry_price"]),
            positionValue=str(pos["size"] * pos["entry_price"]),
            unrealisedPnl="0",
            createdTime=str(pos["entry_time"]),
            updatedTime=str(pos["entry_time"]),
        ))

    return PositionListResponse(
        retCode=0,
        retMsg="OK",
        result=PositionListResult(category=category, list=positions),
        retExtInfo={},
        time=int(time.time() * 1000),
    )

# ============================================================
# Kline
# ============================================================

@router.get("/market/kline", response_model=KlineResponse)
def market_kline(
    category: str,
    symbol: str,
    interval: str,
    limit: int = 3,
    state: ExchangeState = Depends(get_state),
) -> KlineResponse:
    """
    Свечи до current_idx.

    Bybit отдаёт от НОВЫХ к СТАРЫМ — сохраняем этот порядок.
    current_idx += 1 (двигаем время).
    """

    # Проверка, чтобы хватило свечей для прогрева
    if state.current_idx < limit:
        state.current_idx = limit

    # Последние limit свечей до idx
    chunk = state.candles[state.current_idx - limit:state.current_idx]

    # Bybit-формат свечи: [start, open, high, low, close, volume, turnover]
    # Порядок: от новых к старым
    klines = []
    # for c in reversed(chunk):
    for c in chunk:
        klines.append([
            str(c["timestamp"]),
            str(c["open"]),
            str(c["high"]),
            str(c["low"]),
            str(c["close"]),
            str(c["volume"]),
            "0",  # turnover — не считаем
        ])

    return KlineResponse(
        retCode=0,
        retMsg="OK",
        result=KlineResult(symbol=symbol, category=category, list=klines),
        retExtInfo={},
        time=int(time.time() * 1000),
    )


@router.post("/order/create", response_model=OrderCreateResponse)
async def order_create(
        request: Request,
        state: ExchangeState = Depends(get_state),
        x_bapi_api_key: str | None = Header(None, alias="X-BAPI-API-KEY"),
        x_bapi_sign: str | None = Header(None, alias="X-BAPI-SIGN"),
        x_bapi_timestamp: str | None = Header(None, alias="X-BAPI-TIMESTAMP"),
        x_bapi_recv_window: str | None = Header(None, alias="X-BAPI-RECV-WINDOW"),
) -> OrderCreateResponse:
    body = await request.json()

    req = OrderCreateRequest(**body)

    order_id = str(uuid.uuid4())
    now_ms = state.candles[state.current_idx]["timestamp"]

    # === Сохраняем ордер в state ===
    order = {
        "orderId": order_id,
        "orderLinkId": req.orderLinkId or "",
        "category": req.category,
        "symbol": req.symbol,
        "side": req.side,
        "orderType": req.orderType,
        "qty": req.qty,
        "price": req.price,
        "triggerPrice": req.triggerPrice,
        "triggerBy": req.triggerBy,
        "triggerDirection": req.triggerDirection,
        "reduceOnly": req.reduceOnly,
        "timeInForce": req.timeInForce,
        "createdAt": now_ms,
        "status": "New",
    }

    # ============================================================
    # 1. МАРКЕТ ОРДЕР (без триггера) — исполняем СРАЗУ
    # ============================================================
    if req.orderType == "Market" and req.triggerPrice is None:
        # Подменяем triggerPrice на open текущей свечи для process_order
        order["triggerPrice"] = str(state.candles[state.current_idx]["open"])

        # Добавляем в историю (для графика), но НЕ в активные
        state.orders_history.append(order)

        # Вызываем диспетчер напрямую
        from app.services.orders import process_order
        process_order(state, order)

    # ============================================================
    # 2. ТРИГГЕРНЫЙ ОРДЕР — сохраняем и ждём
    # ============================================================
    elif req.triggerPrice is not None:
        state.orders.append(order)
        state.orders_history.append(order)

    return OrderCreateResponse(
        retCode=0,
        retMsg="OK",
        result=OrderResult(orderId=order_id, orderLinkId=order["orderLinkId"]),
        retExtInfo={},
        time=now_ms,
    )

@router.post("/debug/open")
def debug_open(
    side: str = "long",
    symbol: str = "BTCUSDT",
    size: float = 0.001,
    price: float = 114600.0,
    state: ExchangeState = Depends(get_state),
):
    from app.services.positions import open_position
    open_position(state, side, size, symbol, price)
    return state.position
