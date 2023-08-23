import ccxt
import pandas as pd
import ta
import numpy as np

# Создание экземпляра Binance API
exchange = ccxt.binance()

# Настройка параметров для подключения к WebSocket
symbol = 'BTC/USDT'
timeframe = '5m'
rsi_length = 14

# Список для хранения цен закрытия свечей
last_prices = []


# Функция обработки сообщений от WebSocket
def on_message(ws, message):
    global last_prices

    # Преобразование сообщения в словарь
    data = eval(message)

    # Получение цены закрытия из сообщения
    close_price = float(data['k']['c'])
    last_prices.append(close_price)

    if len(last_prices) >= rsi_length:
        # Создание DataFrame с ценами закрытия
        df = pd.DataFrame({'close': last_prices})

        # Расчет RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], rsi_length).rsi()

        print(df.tail())
        # Можете выполнить здесь другие действия с данными, например, сигналы на основе RSI

        # Очистка списка цен закрытия для управления памятью
        last_prices.pop(0)


# Подключение к WebSocket
def main():
    ws = exchange.watch_kline(symbol, timeframe)
    ws.on_message = on_message
    ws.run_forever()


if __name__ == "__main__":
    main()
