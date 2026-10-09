# app/routers/position.py
"""GET /position — текущая позиция."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_state
from app.models.responses import PositionResponse, Position
from app.services.state import ExchangeState


router = APIRouter(tags=["trading"])


@router.get("/position", response_model=PositionResponse)
def get_position(state: ExchangeState = Depends(get_state)) -> PositionResponse:
    if state.position is None:
        return PositionResponse(position=None)
    return PositionResponse(position=Position(**state.position))