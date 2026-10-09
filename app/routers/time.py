# app/routers/time.py
"""POST /next — сдвинуть свечу. POST /reset — сброс."""

from fastapi import APIRouter, Depends

from config import COMMISSION_PCT
from app.core.dependencies import get_state
from app.models.requests import NextRequest, ResetRequest
from app.models.responses import NextResponse, ResetResponse
from app.services.state import ExchangeState
from app.services.candles import next_candle, is_finished
from app.services.orders import check_sl_tp
from app.services.trades import record_equity


router = APIRouter(tags=["time"])


@router.post("/next", response_model=NextResponse)
def move_next(
    req: NextRequest,
    state: ExchangeState = Depends(get_state),
) -> NextResponse:
    for _ in range(req.count):
        # 1. Сдвинуть указатель
        moved = next_candle(state)
        if not moved:
            break

        # 2. Проверить SL/TP на новой свече
        check_sl_tp(state, COMMISSION_PCT)

        # 3. Записать equity
        record_equity(state)

    return NextResponse(
        status="ok",
        current_idx=state.current_idx,
        total=len(state.candles),
        finished=is_finished(state),
    )


@router.post("/reset", response_model=ResetResponse)
def reset(
    req: ResetRequest,
    state: ExchangeState = Depends(get_state),
) -> ResetResponse:
    state.reset()
    return ResetResponse(
        status="ok",
        balance=state.balance,
        current_idx=state.current_idx,
    )