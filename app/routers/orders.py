# app/routers/orders.py
"""POST /order — выставить ордер. POST /cancel — отменить."""

from fastapi import APIRouter, Depends

from config import COMMISSION_PCT
from app.core.dependencies import get_state
from app.models.requests import OrderRequest
from app.models.responses import OrderResponse
from app.services.state import ExchangeState
from app.services.orders import open_position, close_position


router = APIRouter(tags=["trading"])


@router.post("/order", response_model=OrderResponse)
def create_order(
    req: OrderRequest,
    state: ExchangeState = Depends(get_state),
) -> OrderResponse:
    # Если позиция открыта — закрываем (упрощённо: один ордер = одно действие)
    if state.position is not None:
        result = close_position(state, COMMISSION_PCT)
    else:
        result = open_position(
            state,
            side=req.side,
            size=req.size,
            commission_pct=COMMISSION_PCT,
            sl=req.sl,
            tp=req.tp,
        )
    return OrderResponse(**result)


@router.post("/cancel", response_model=OrderResponse)
def cancel_order() -> OrderResponse:
    # Заглушка — активных ордеров пока нет
    return OrderResponse(status="ok", error=None)