import websocket
import json
import pandas as pd

# Настройки для подключения к WebSocket API Bitfinex
symbol = 'tBTCUSD'  # Валютная пара BTC/USD
timeframe = '1m'  # 1 минута
vwap_window = 20  # Окно для расчета VWAP

# Списки для хранения данных
trade_prices = []
trade_volumes = []


# Функция обработки сообщений от WebSocket
def on_message(ws, message):
    global trade_prices, trade_volumes

    data = json.loads(message)

    # Проверяем, что сообщение содержит данные о сделках
    if isinstance(data, list) and isinstance(data[1], list):
        trade_price = float(data[1][7])  # Цена сделки
        trade_volume = float(data[1][2])  # Объем сделки

        trade_prices.append(trade_price)
        trade_volumes.append(trade_volume)

        if len(trade_prices) >= vwap_window:
            # Создаем DataFrame с данными
            df = pd.DataFrame({'price': trade_prices, 'volume': trade_volumes})

            # Рассчитываем VWAP
            df['vwap'] = (df['price'] * df['volume']).cumsum() / df['volume'].cumsum()

            print(df.tail(1))

            # Убираем старые данные
            trade_prices.pop(0)
            trade_volumes.pop(0)


# Подключение к WebSocket
def main():
    url = f'wss://api-pub.bitfinex.com/ws/2/trade:{symbol}:{timeframe}'
    ws = websocket.WebSocketApp(url, on_message=on_message)
    ws.run_forever()


if __name__ == "__main__":
    main()
