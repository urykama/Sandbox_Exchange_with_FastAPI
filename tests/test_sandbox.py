import pytest
from app.services.state import ExchangeState
from app.services.orders import process_order, check_triggers, check_limit_orders

@pytest.fixture
def state():
    """Стейт с 5 свечами и балансом 10000."""
    s = ExchangeState(initial_balance=10000.0)
    s.candles = [
        {"timestamp": 1000, "open": 100.0, "high": 105.0, "low": 95.0,  "close": 100.0, "volume": 10},
        {"timestamp": 2000, "open": 100.0, "high": 110.0, "low": 90.0,  "close": 100.0, "volume": 10},
        {"timestamp": 3000, "open": 100.0, "high": 120.0, "low": 80.0,  "close": 100.0, "volume": 10},
    ]
    s.current_idx = 0
    return s

# ==========================================
# 1. Открытие и закрытие по МАРКЕТУ
# ==========================================
def test_market_open_long(state):
    order = {"symbol": "BTCUSDT", "side": "Buy", "qty": "1", "triggerPrice": "100.0"}
    process_order(state, order)
    
    assert state.position is not None
    assert state.position["side"] == "long"
    assert state.position["size"] == 1.0
    assert state.position["entry_price"] == 100.0
    assert state.balance == 9900.0  # 10000 - 100

def test_market_close_long(state):
    # Открываем
    process_order(state, {"symbol": "BTCUSDT", "side": "Buy", "qty": "1", "triggerPrice": "100.0"})
    
    # Закрываем маркетом по 110
    process_order(state, {"symbol": "BTCUSDT", "side": "Sell", "qty": "1", "triggerPrice": "110.0"})
    
    assert state.position is None
    assert state.balance == 10010.0  # 9900 + (1*100) + 10 (pnl)
    assert len(state.trades) == 1
    assert state.trades[0]["pnl"] == 10.0

# ==========================================
# 2. Разворот
# ==========================================
def test_reversal(state):
    # Long 1
    process_order(state, {"symbol": "BTCUSDT", "side": "Buy", "qty": "1", "triggerPrice": "100.0"})
    # Приходит Sell 1
    process_order(state, {"symbol": "BTCUSDT", "side": "Sell", "qty": "2", "triggerPrice": "110.0"})
    
    assert state.position is not None
    assert state.position["side"] == "short"
    assert state.position["size"] == 1.0
    assert state.position["entry_price"] == 110.0
    # Баланс: закрыли лонг (+10), открыли шорт (-110)
    assert state.balance == 9900.0  # 9900 + 110 - 110

# ==========================================
# 3. Частичное закрытие
# ==========================================
def test_partial_close(state):
    # Long 2
    process_order(state, {"symbol": "BTCUSDT", "side": "Buy", "qty": "2", "triggerPrice": "100.0"})
    # Sell 1
    process_order(state, {"symbol": "BTCUSDT", "side": "Sell", "qty": "1", "triggerPrice": "105.0"})
    
    assert state.position is not None
    assert state.position["size"] == 1.0  # Остаток
    assert state.balance == 9905.0

# ==========================================
# 4. Лимитный ордер
# ==========================================
def test_limit_order(state):
    # Вешаем лимит Buy 1 @ 90
    order = {
        "symbol": "BTCUSDT", "side": "Buy", "qty": "1", 
        "price": "90.0", "orderType": "Limit", "triggerPrice": None
    }
    state.orders.append(order)
    
    # Свеча 0: low=95. Не исполняется.
    check_limit_orders(state)
    assert len(state.orders) == 1
    assert state.position is None
    
    # Свеча 1: low=90. Исполняется.
    state.current_idx = 1
    check_limit_orders(state)
    assert len(state.orders) == 0
    assert state.position is not None
    assert state.position["entry_price"] == 90.0

# ==========================================
# 5. Триггерный ордер
# ==========================================
def test_trigger_order(state):
    # Вешаем триггер Sell 1 @ 105
    order = {
        "symbol": "BTCUSDT", "side": "Sell", "qty": "1", 
        "triggerPrice": "105.0", "orderType": "Market"
    }
    state.orders.append(order)
    
    # Свеча 0: high=105. Срабатывает.
    check_triggers(state)
    assert len(state.orders) == 0
    assert state.position is not None
    assert state.position["side"] == "short"
    assert state.position["entry_price"] == 105.0

# ==========================================
# 6. Частичное закрытие лимитным ордером
# ==========================================
def test_limit_partial_close(state):
    # 1. Открываем Long 2 маркетом
    process_order(state, {"symbol": "BTCUSDT", "side": "Buy", "qty": "2", "triggerPrice": "100.0"})
    assert state.position["size"] == 2.0

    # 2. Вешаем лимит Sell 1 @ 110
    order = {
        "symbol": "BTCUSDT", "side": "Sell", "qty": "1", 
        "price": "108.0", "orderType": "Limit", "triggerPrice": None
    }
    state.orders.append(order)

    # 3. Свеча 0: high=105. Не исполняется (105 < 110).
    check_limit_orders(state)
    assert state.position["size"] == 2.0
    assert len(state.orders) == 1

    # 4. Свеча 1: high=110. Исполняется. Должен закрыть 1.
    state.current_idx = 1
    check_limit_orders(state)
    
    # 5. Проверяем, что позиция уменьшилась до 1.0
    assert state.position["size"] == 1.0
    assert state.position["side"] == "long"
    assert state.orders == []  # ордер исполнен и удален

    # 6. Вешаем ещё один лимит Sell 2 @ 105
    order2 = {
        "symbol": "BTCUSDT", "side": "Sell", "qty": "2", 
        "price": "118.0", "orderType": "Limit", "triggerPrice": None
    }
    state.orders.append(order2)

    # 7. Свеча 2: low=80. Исполняется (80 <= 105).
    state.current_idx = 2
    check_limit_orders(state)

    # 8. Проверяем разворот:
    #    - Закрыли остаток long 1.0 (по 105)
    #    - Открыли short 1.0 (остаток от 2.0)
    assert state.position is not None
    assert state.position["side"] == "short"
    assert state.position["size"] == 1.0
    
    # Проверяем, что оба ордера ушли из очереди
    assert state.orders == []