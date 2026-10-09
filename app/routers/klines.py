# app/routers/klines.py
"""GET /klines — свечи до текущего указателя."""

from fastapi import APIRouter, Depends, Query

from config import SYMBOL, KLINES_DEFAULT_LIMIT, KLINES_MAX_LIMIT
from app.core.dependencies import get_state
from app.models.responses import KlinesResponse, Candle
from app.services.state import ExchangeState
from app.services.candles import get_klines


router = APIRouter(tags=["market"])


@router.get("/klines", response_model=KlinesResponse)
def klines(
    limit: int = Query(KLINES_DEFAULT_LIMIT, ge=1, le=KLINES_MAX_LIMIT),
    state: ExchangeState = Depends(get_state),
) -> KlinesResponse:
    candles = get_klines(state, limit)
    return KlinesResponse(
        symbol=state.symbol,
        candles=[Candle(**c) for c in candles],
        current_idx=state.current_idx,
    )