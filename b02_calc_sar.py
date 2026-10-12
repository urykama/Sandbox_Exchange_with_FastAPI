# b02_calc_sar.py
"""
Расчёт SAR для всех свечей в Candles/.
Сохраняет в Candles_with_SAR/.
"""

import os
import pandas as pd

from config import CANDLES_FOLDER, CANDLES_SAR_FOLDER

from calculate_parabolic_sar import calculate_parabolic_sar


def process_file(path, output_folder):
    """Читает CSV, считает SAR, сохраняет."""
    if not os.path.exists(path):
        print(f"❌ Файл не найден: {path}")
        return False

    df = pd.read_csv(path)

    # Проверяем колонки
    required = ['high', 'low', 'close']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"⚠️ {path}: нет колонок {missing}")
        return False

    if len(df) < 2:
        print(f"⚠️ {path}: меньше 2 строк")
        return False

    # Считаем SAR
    df = calculate_parabolic_sar(df)

    # Сохраняем
    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.basename(path)
    name, ext = os.path.splitext(base_name)
    output_path = os.path.join(output_folder, f"{name}_sar{ext}")

    df.to_csv(output_path, index=False)
    print(f"✅ {base_name} → {output_path} ({len(df)} строк)")

    return True


def main():
    if not os.path.isdir(CANDLES_FOLDER):
        print(f"❌ Папка не найдена: {CANDLES_FOLDER}")
        return

    count = 0
    for root, dirs, files in os.walk(CANDLES_FOLDER):
        for file in files:
            if file.endswith(".csv"):
                path = os.path.join(root, file)
                if process_file(path, CANDLES_SAR_FOLDER):
                    count += 1

    print(f"📊 Обработано: {count}")


if __name__ == '__main__':
    main()