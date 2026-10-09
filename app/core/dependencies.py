# app/core/dependencies.py
"""
Общие зависимости FastAPI.

Один экземпляр ExchangeState на всё приложение.
Создаётся при старте, живёт до перезапуска.
"""

from app.services.state import ExchangeState


# Единственный объект состояния
_state: ExchangeState | None = None


def get_state() -> ExchangeState:
    """Вернуть текущее состояние. Создать при первом запросе."""
    global _state
    if _state is None:
        _state = ExchangeState()
    return _state