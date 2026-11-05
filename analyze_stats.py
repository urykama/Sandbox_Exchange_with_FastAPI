import pandas as pd


def analyze(trades_path="data/Results/trades.csv", initial_balance=1000.0):
    try:
        df = pd.read_csv(trades_path)
    except FileNotFoundError:
        print(f"Файл не найден: {trades_path}")
        return

    if df.empty:
        print("Нет сделок.")
        return

    # 1. Считаем серии и собираем статистику по их длинам
    max_loss_streak = 0
    current_loss_streak = 0
    max_win_streak = 0
    current_win_streak = 0

    loss_streaks_count = {}
    win_streaks_count = {}

    pnl_list = df['pnl'].tolist()

    for pnl in pnl_list:
        if pnl < 0:
            current_loss_streak += 1
            if current_win_streak > 0:
                # Закончилась серия прибылей
                win_streaks_count[current_win_streak] = win_streaks_count.get(current_win_streak, 0) + 1
                current_win_streak = 0

            if current_loss_streak > max_loss_streak:
                max_loss_streak = current_loss_streak

        elif pnl > 0:
            current_win_streak += 1
            if current_loss_streak > 0:
                # Закончилась серия убытков
                loss_streaks_count[current_loss_streak] = loss_streaks_count.get(current_loss_streak, 0) + 1
                current_loss_streak = 0

            if current_win_streak > max_win_streak:
                max_win_streak = current_win_streak
        else:
            # Если ровно 0, обнуляем обе серии
            if current_loss_streak > 0:
                loss_streaks_count[current_loss_streak] = loss_streaks_count.get(current_loss_streak, 0) + 1
                current_loss_streak = 0
            if current_win_streak > 0:
                win_streaks_count[current_win_streak] = win_streaks_count.get(current_win_streak, 0) + 1
                current_win_streak = 0

    # Не забываем записать серии, если они не закончились к концу файла
    if current_loss_streak > 0:
        loss_streaks_count[current_loss_streak] = loss_streaks_count.get(current_loss_streak, 0) + 1
    if current_win_streak > 0:
        win_streaks_count[current_win_streak] = win_streaks_count.get(current_win_streak, 0) + 1

    # 2. Считаем просадки (Drawdowns)
    if 'balance' in df.columns:
        balances = [initial_balance] + df['balance'].tolist()
    else:
        balances = [initial_balance]
        current = initial_balance
        for pnl in df['pnl']:
            current += pnl
            balances.append(current)

    peak = balances[0]
    drawdown_events = 0
    in_drawdown = False
    max_drawdown_pct = 0

    for b in balances:
        if b > peak:
            peak = b
            if in_drawdown:
                in_drawdown = False
        else:
            dd_pct = (peak - b) / peak * 100
            if dd_pct > max_drawdown_pct:
                max_drawdown_pct = dd_pct

            # Если просадка больше 20% и мы еще не отметили это событие
            if dd_pct >= 20 and not in_drawdown:
                drawdown_events += 1
                in_drawdown = True

    # --- ВЫВОД ---
    print("=" * 50)
    print(" 📊 ГЛУБОКАЯ СТАТИСТИКА ПО СДЕЛКАМ")
    print("=" * 50)
    print(f" Всего сделок:           {len(df)}")
    print(f" Макс. серия убытков:    {max_loss_streak} подряд")
    print(f" Макс. серия прибылей:   {max_win_streak} подряд")
    print("-" * 50)
    print(f" Макс. просадка:         -{max_drawdown_pct:.2f}%")
    print(f" Просадок > 20%:         {drawdown_events} раз")

    print("-" * 50)
    print(" 📉 СЕРИИ УБЫТКОВ (сколько раз подряд было):")
    for length in sorted(loss_streaks_count.keys()):
        print(f"   - {length} подряд: {loss_streaks_count[length]} раз")

    print("-" * 50)
    print(" 📈 СЕРИИ ПРИБЫЛЕЙ (сколько раз подряд было):")
    for length in sorted(win_streaks_count.keys()):
        print(f"   - {length} подряд: {win_streaks_count[length]} раз")
    print("=" * 50)


if __name__ == "__main__":
    analyze(initial_balance=1000.0)

"""
==================================================
 📊 ГЛУБОКАЯ СТАТИСТИКА ПО СДЕЛКАМ
==================================================
 Всего сделок:           371
 Макс. серия убытков:    7 подряд
 Макс. серия прибылей:   4 подряд
--------------------------------------------------
 Макс. просадка:         -36.27%
 Просадок > 20%:         3 раз
--------------------------------------------------
 📉 СЕРИИ УБЫТКОВ (сколько раз подряд было):
   - 1 подряд: 44 раз
   - 2 подряд: 25 раз
   - 3 подряд: 15 раз
   - 4 подряд: 6 раз
   - 5 подряд: 3 раз
   - 6 подряд: 5 раз
   - 7 подряд: 3 раз
--------------------------------------------------
 📈 СЕРИИ ПРИБЫЛЕЙ (сколько раз подряд было):
   - 1 подряд: 71 раз
   - 2 подряд: 21 раз
   - 3 подряд: 7 раз
   - 4 подряд: 2 раз
==================================================
"""