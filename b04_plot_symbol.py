# b04_plot_symbol.py
"""График: свечи + SAR + EP + сделки."""

import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CANDLES_SAR_FOLDER, TIMEFRAME, TRADES_PATH


def plot_symbol(symbol):
    # 1. Свечи + SAR
    path = os.path.join(CANDLES_SAR_FOLDER, f"{TIMEFRAME}_sar.csv")
    if not os.path.exists(path):
        print(f"❌ Файл не найден: {path}")
        return

    df = pd.read_csv(path)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    dates = df['datetime'].tolist()

    # Индекс по timestamp — чтобы быстро найти свечу
    ts_to_idx = {int(t): i for i, t in enumerate(df['timestamp'])}

    # 2. Сделки
    if not os.path.exists(TRADES_PATH):
        print(f"❌ Нет trades.csv: {TRADES_PATH}")
        return

    trades = pd.read_csv(TRADES_PATH)
    symbol_trades = trades[trades['symbol'] == symbol]

    if symbol_trades.empty:
        print(f"⚠️ Нет сделок по {symbol}")
        return

    total_pnl = symbol_trades['pnl'].sum()

    # 3. Фигура
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        subplot_titles=(
            f"{symbol} | Сделок: {len(symbol_trades)} | PnL: {total_pnl:.2f} USDT",
            "Volume",
        ),
    )

    # 4. Свечи
    fig.add_trace(go.Candlestick(
        x=dates,
        open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        name='Close',
        increasing_line_color='green',
        decreasing_line_color='red',
    ), row=1, col=1)

    # 5. SAR
    if 'sar' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['sar'],
            name='SAR',
            line=dict(color='orange', width=1, dash='dot'),
        ), row=1, col=1)

    # 6. EP
    if 'ep' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['ep'],
            name='EP',
            line=dict(color='green', width=1),
            opacity=0.4,
        ), row=1, col=1)

    # 7. Сделки
    entry_x, entry_y, entry_text, entry_color = [], [], [], []
    exit_x, exit_y, exit_text, exit_color = [], [], [], []
    lines_x, lines_y = [], []

    for _, t in symbol_trades.iterrows():
        entry_ts = int(t['entry_time'])
        exit_ts  = int(t['exit_time'])

        entry_idx = ts_to_idx.get(entry_ts)
        exit_idx  = ts_to_idx.get(exit_ts)

        if entry_idx is None or exit_idx is None:
            continue

        entry_dt = dates[entry_idx]
        exit_dt  = dates[exit_idx]

        entry_price = t['entry_price']
        exit_price  = t['exit_price']
        pnl         = t['pnl']
        side        = t['side']            # 'long' / 'short'

        # Вход
        entry_x.append(entry_dt)
        entry_y.append(entry_price)
        entry_text.append('LONG' if side == 'long' else 'SHORT')
        entry_color.append('blue' if side == 'long' else 'purple')

        # Выход
        exit_x.append(exit_dt)
        exit_y.append(exit_price)
        exit_text.append(f"{pnl:+.2f}")
        exit_color.append('green' if pnl > 0 else 'red')

        # Линия
        lines_x.extend([entry_dt, exit_dt, None])
        lines_y.extend([entry_price, exit_price, None])

    # Линии
    fig.add_trace(go.Scatter(
        x=lines_x, y=lines_y,
        mode='lines',
        line=dict(color='gray', width=1),
        name='Trades',
        showlegend=False,
        opacity=0.5,
    ), row=1, col=1)

    # Входы
    fig.add_trace(go.Scatter(
        x=entry_x, y=entry_y,
        mode='markers',
        marker=dict(color=entry_color, size=8, symbol='triangle-up'),
        name='Entry',
        text=entry_text,
        hovertemplate='%{text}<br>Entry: %{y:.2f}<extra></extra>',
    ), row=1, col=1)

    # Выходы
    fig.add_trace(go.Scatter(
        x=exit_x, y=exit_y,
        mode='markers',
        marker=dict(color=exit_color, size=8, symbol='x'),
        name='Exit',
        text=exit_text,
        hovertemplate='Exit: %{y:.2f}<br>PnL: %{text}<extra></extra>',
    ), row=1, col=1)

    # 8. Volume
    fig.add_trace(go.Bar(
        x=dates, y=df['volume'],
        name='Volume',
        marker_color='gray',
    ), row=2, col=1)

    # 9. Настройки
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=900,
        hovermode='x unified',
        template='plotly_dark',
        xaxis=dict(type='date', constrain='domain', rangeslider=dict(visible=False)),
        xaxis2=dict(type='date', constrain='domain', rangeslider=dict(visible=False)),
    )

    # 10. Сохраняем
    os.makedirs('Charts', exist_ok=True)
    out = f"Charts/{symbol}_all.html"
    fig.write_html(out, include_plotlyjs='cdn')
    print(f"📊 График: {out}")
    fig.show()


if __name__ == '__main__':
    plot_symbol('BTCUSDT')