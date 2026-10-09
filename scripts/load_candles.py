# scripts/load_candles.py
"""
Загрузка свечей с Binance.

Идём НАЗАД по времени: сначала последние 1000,
потом предыдущие 1000 и т.д., пока не наберём target.

Сохраняет в: data/Candles_Binance/<SYMBOL>/<TIMEFRAME>.csv

Запуск:
    python -m scripts.load_candles
"""

import csv
import time
from pathlib import Path

import requests

from config import (
    SYMBOL,
    TIMEFRAME,
    CANDLES_FOLDER,
    CANDLES_TARGET_COUNT,
    BINANCE_API_URL,
    BINANCE_KLINES_LIMIT,
    BINANCE_REQUEST_PAUSE,
)


# ============================================================
# Запрос к Binance
# ============================================================

def fetch_klines(symbol: str, interval: str, limit: int, end_time: int | None = None) -> list:
    """Один запрос. end_time — докуда (мс). None — до текущего момента."""
    url = f"{BINANCE_API_URL}/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    if end_time is not None:
        params["endTime"] = end_time

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def normalize(raw: list) -> list[dict]:
    """Binance → наш формат."""
    out = []
    for k in raw:
        out.append({
            "timestamp": int(k[0]),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
        })
    return out


# ============================================================
# Пагинация назад
# ============================================================

def load_all(symbol: str, interval: str, target: int) -> list[dict]:
    """Собирает target свечей, идя назад от текущего момента."""
    all_candles: list[dict] = []
    end_time: int | None = None

    while len(all_candles) < target:
        raw = fetch_klines(symbol, interval, BINANCE_KLINES_LIMIT, end_time)
        if not raw:
            break

        candles = normalize(raw)
        # Binance отдаёт по возрастанию, добавляем в НАЧАЛО
        all_candles = candles + all_candles

        first_ts = candles[0]["timestamp"]
        print(f"   получено: {len(all_candles):>7} (первая: {first_ts})")

        # Следующий запрос — ДО первой свечи
        end_time = first_ts - 1

        if len(raw) < BINANCE_KLINES_LIMIT:
            break

        time.sleep(BINANCE_REQUEST_PAUSE)

    return all_candles


# ============================================================
# Сохранение
# ============================================================

def save_csv(candles: list[dict], path: Path) -> None:
    """Сохраняет свечи в CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "open", "high", "low", "close", "volume"],
        )
        writer.writeheader()
        writer.writerows(candles)


# ============================================================
# Точка входа
# ============================================================

def main() -> None:
    print(f"📥 Загрузка {SYMBOL} {TIMEFRAME}")
    print(f"   цель: {CANDLES_TARGET_COUNT} свечей")
    print()

    candles = load_all(SYMBOL, TIMEFRAME, CANDLES_TARGET_COUNT)

    if not candles:
        print("❌ Ничего не загружено")
        return

    # Дедупликация + сортировка
    seen = set()
    unique = []
    for c in candles:
        if c["timestamp"] not in seen:
            seen.add(c["timestamp"])
            unique.append(c)
    unique.sort(key=lambda x: x["timestamp"])

    path = Path(CANDLES_FOLDER) / SYMBOL / f"{TIMEFRAME}.csv"
    save_csv(unique, path)

    print()
    print(f"✅ Сохранено: {len(unique)} свечей")
    print(f"   файл: {path}")
    print(f"   первая: {unique[0]['timestamp']}")
    print(f"   последняя: {unique[-1]['timestamp']}")


if __name__ == "__main__":
    main()