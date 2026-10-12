# app/main.py
"""Sandbox Exchange — Bybit-совместимый."""

from fastapi import FastAPI

from config import PROJECT_NAME, VERSION, CANDLES_PATH
from app.core.dependencies import get_state
from app.services.candles import load_candles
from app.exchanges.bybit import router as bybit_router


# Загрузка свечей при старте
state = get_state()
try:
    n = load_candles(state, CANDLES_PATH)
    print(f"✅ Загружено свечей: {n} из {CANDLES_PATH}")
except FileNotFoundError as e:
    print(f"⚠️  {e}")


app = FastAPI(title=PROJECT_NAME, version=VERSION)

app.include_router(bybit_router.router)