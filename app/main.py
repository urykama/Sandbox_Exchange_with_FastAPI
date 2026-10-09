# app/main.py
"""
Создание FastAPI-приложения.

Только:
- создание app
- подключение роутеров
- стартовая загрузка свечей
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from config import PROJECT_NAME, VERSION, MODE, CANDLES_PATH
from app.core.dependencies import get_state
from app.services.candles import load_candles


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: загрузить свечи в state
    state = get_state()
    try:
        n = load_candles(state, CANDLES_PATH)
        print(f"✅ Загружено свечей: {n} из {CANDLES_PATH}")
    except FileNotFoundError as e:
        print(f"⚠️  {e}")
    yield
    # Shutdown: ничего


app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="Тестовый двойник биржевого API для бэктестов стратегий.",
    lifespan=lifespan,
)


# === Роутеры ===
from app.routers import health, klines, orders, position, time

app.include_router(health.router)
app.include_router(klines.router)
app.include_router(orders.router)
app.include_router(position.router)
app.include_router(time.router)