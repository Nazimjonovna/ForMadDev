import ccxt
import websocket
import json
import pandas as pd
import numpy as np
import threading

binance_symbol = 'BTC/USDT'
binance_timeframe = '5m'
rsi_length = 14
binance_close_prices = []


bitfinex_symbol = 'tBTCUSD'
bitfinex_timeframe = '1m'
vwap_window = 20
bitfinex_trade_prices = []
bitfinex_trade_volumes = []


binance_lock = threading.Lock()
bitfinex_lock = threading.Lock()


def binance_on_message(ws, message):
    global binance_close_prices

    data = json.loads(message)

    if 'k' in data:
        close_price = float(data['k']['c'])

        binance_lock.acquire()
        binance_close_prices.append(close_price)
        binance_lock.release()



def bitfinex_on_message(ws, message):
    global bitfinex_trade_prices, bitfinex_trade_volumes

    data = json.loads(message)

    if isinstance(data, list) and isinstance(data[1], list):
        trade_price = float(data[1][7])
        trade_volume = float(data[1][2])

        bitfinex_lock.acquire()
        bitfinex_trade_prices.append(trade_price)
        bitfinex_trade_volumes.append(trade_volume)
        bitfinex_lock.release()



def calculate_indicators():
    global binance_close_prices, bitfinex_trade_prices, bitfinex_trade_volumes

    while True:
        if len(binance_close_prices) >= rsi_length:
            binance_lock.acquire()
            binance_prices = np.array(binance_close_prices)
            binance_lock.release()

            binance_rsi = ta.momentum.RSIIndicator(binance_prices, rsi_length).rsi()
            print(f"Binance - Close: {binance_prices[-1]}, RSI: {binance_rsi[-1]}")

        if len(bitfinex_trade_prices) >= vwap_window:
            bitfinex_lock.acquire()
            bitfinex_prices = np.array(bitfinex_trade_prices)
            bitfinex_volumes = np.array(bitfinex_trade_volumes)
            bitfinex_lock.release()

            bitfinex_vwap = (bitfinex_prices * bitfinex_volumes).cumsum() / bitfinex_volumes.cumsum()
            print(f"Bitfinex - Close: {bitfinex_prices[-1]}, VWAP: {bitfinex_vwap[-1]}")


        time.sleep(60)  # Подождите 1 минуту



binance_ws_url = f'wss://stream.binance.com:9443/ws/{binance_symbol.lower()}@kline_{binance_timeframe}'
bitfinex_ws_url = f'wss://api-pub.bitfinex.com/ws/2/trade:{bitfinex_symbol}:{bitfinex_timeframe}'

binance_ws = websocket.WebSocketApp(binance_ws_url, on_message=binance_on_message)
bitfinex_ws = websocket.WebSocketApp(bitfinex_ws_url, on_message=bitfinex_on_message)


binance_thread = threading.Thread(target=binance_ws.run_forever)
bitfinex_thread = threading.Thread(target=bitfinex_ws.run_forever)
indicator_thread = threading.Thread(target=calculate_indicators)

binance_thread.start()
bitfinex_thread.start()
indicator_thread.start()

binance_thread.join()
bitfinex_thread.join()
indicator_thread.join()
