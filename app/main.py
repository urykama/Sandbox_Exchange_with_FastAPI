# app/main.py
"""
Создание FastAPI-приложения.

Здесь только:
- создание app
- подключение роутеров
- базовые настройки (title, version)

Вся логика — в routers/ и services/.
"""

from fastapi import FastAPI

from config import PROJECT_NAME, VERSION, MODE


app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="Тестовый двойник биржевого API для бэктестов стратегий.",
)


# ============================================================
# Health check
# ============================================================

@app.get("/health", tags=["system"])
def health() -> dict:
    """Проверка живости сервера."""
    return {
        "status": "ok",
        "project": PROJECT_NAME,
        "version": VERSION,
        "mode": MODE,
    }


# ============================================================
# Роутеры (подключим позже, по мере готовности)
# ============================================================

# from app.routers import klines, orders, position, time
# app.include_router(klines.router)
# app.include_router(orders.router)
# app.include_router(position.router)
# app.include_router(time.router)