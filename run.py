# run.py
"""Точка входа Sandbox Exchange."""

import os

import uvicorn

from config import (
    PROJECT_NAME,
    VERSION,
    MODE,
    API_HOST,
    API_PORT,
    API_RELOAD,
    CANDLES_FOLDER,
    RESULTS_FOLDER,
)


def ensure_folders() -> None:
    os.makedirs(CANDLES_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)

def print_banner() -> None:
    line = "=" * 60
    print(line)
    print(f"  {PROJECT_NAME}")
    print(f"  Version: {VERSION}")
    print(f"  Mode:    {MODE}")
    print(line)
    print(f"  API:     http://{API_HOST}:{API_PORT}")
    print(f"  Docs:    http://127.0.0.1:{API_PORT}/docs")
    print(line)
    print(flush=True)


def main() -> None:
    ensure_folders()
    print_banner()

    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        access_log=False,        # ← добавить
    )


if __name__ == "__main__":
    main()

"""
==================================================
 📊 СТАТИСТИКА ТЕСТ-БИРЖИ
==================================================
 💰 Начальный баланс: 1000.00 USDT
 💰 Финальный баланс: 1061.18 USDT
 📈 Общий PnL:        +61.18 USDT (+6.12%)
--------------------------------------------------
 📉 Всего сделок:     336
 🟢 Прибыльных:       200 (59.5%)
 🔴 Убыточных:        136 (40.5%)
--------------------------------------------------
 ⚖️  Profit Factor:   1.18
 🟢 Средняя прибыль:  +2.03 USDT
 🔴 Средний убыток:   2.53 USDT
 📉 Max Drawdown:     3.17%
==================================================

==================================================
 📊 СТАТИСТИКА ТЕСТ-БИРЖИ
==================================================
 💰 Начальный баланс: 1000.00 USDT
 💰 Финальный баланс: 6444.62 USDT
 📈 Общий PnL:        +5444.62 USDT (+544.46%)
--------------------------------------------------
 📉 Всего сделок:     380
 🟢 Прибыльных:       293 (77.1%)
 🔴 Убыточных:        87 (22.9%)
--------------------------------------------------
 ⚖️  Profit Factor:   3.25
 🟢 Средняя прибыль:  +26.85 USDT
 🔴 Средний убыток:   27.84 USDT
 📉 Max Drawdown:     18.63%
==================================================
"""