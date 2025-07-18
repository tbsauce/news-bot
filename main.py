import sys
import math
import time
import configparser
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.live.stock import StockDataStream
from alpaca.trading.requests import *
from alpaca.trading.enums import *
from webscraper import get_new_high_priority_tickers

from alpaca.data.requests import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *
import asyncio

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")
api_key = config["keys"]["api_key"]
secret_key = config["keys"]["api_secret"]
paper = True

stock_data_stream_client = StockDataStream(api_key, secret_key)
stock_historical_data_client = StockHistoricalDataClient(api_key, secret_key)
trade_client = TradingClient(api_key, secret_key, paper=paper)

past_requests = {}

async def handler(data):
    symbol = data.symbol 
    close_price = data.price
    print(f"[DATA RECEIVED] {symbol} @ ${close_price:.2f} at {data.timestamp}")

    make_sell_order(symbol, close_price)

async def ticker_handler():
    #Discard 1st symbols
    symbols = get_new_high_priority_tickers()

    while True:
        print("[Log] Getting new Symbols...")
        symbols = get_new_high_priority_tickers()
        symbols = symbols[0:5]
        new_symbols = [s for s in symbols if s not in past_requests]

        if new_symbols:
            for symbol in new_symbols:
                print(f"[Log] Subscribing to {symbol}")
                stock_data_stream_client.subscribe_trades(handler, symbol)
                
                # First buy
                latest_bar = stock_historical_data_client.get_stock_latest_bar(StockLatestBarRequest(symbol_or_symbols=symbol))
                close_price = latest_bar[symbol].close
                make_buy_order(symbol, close_price)
        else:
            print("[Log] No new symbols found")

        await asyncio.sleep(60 * 5)  # Non-blocking wait

def make_sell_order(symbol, close_price):
    uid = past_requests[symbol]["uid"]
    order = trade_client.get_order_by_id(uid)
    if order.status != OrderStatus.FILLED:
        print("[Log] {symbol} not yet filled!")
        return

    take_profit = round(close_price * 2, 2)
    stop_loss = round(close_price * 0.9, 2)
    qty = past_requests[symbol]["qty"] 

    if past_requests[symbol].get("stop_loss", 0) > stop_loss:
        return

    trading_client.cancel_order_by_id(past_requests[symbol]["uid"])
    print("[Log] Cancelled order {symbol}")

    req = StopLimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
        stop_price=stop_loss,
        limit_price=take_profit,
        order_class=OrderClass.SIMPLE,
    )
    order = trade_client.submit_order(req)

    past_requests[symbol]["uid"] = order.id 
    past_requests[symbol]["take_profit"] = take_profit
    past_requests[symbol]["stop_loss"] = stop_loss
    print("[Log] Updated order {symbol}")

def make_buy_order(symbol, close_price):

    account = trade_client.get_account()
    buying_power = float(account.non_marginable_buying_power)
    risk_amount = buying_power * 0.10
    qty = math.floor(risk_amount / close_price)
    stop_price = round(close_price * 1.1, 2)
    limit_price = round(close_price * 1.11, 2)

    req = StopLimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        stop_price=stop_price,
        limit_price=limit_price,
        order_class=OrderClass.SIMPLE
    )
    order = trade_client.submit_order(req)

    past_requests[symbol] = {
        "uid" : order.id,
        "stop_price": stop_price,
        "limit_price": limit_price,
        "qty": qty
    }

# Main async runner
async def main():
        
    stream_task = asyncio.create_task(stock_data_stream_client._run_forever())
    ticker_loop = asyncio.create_task(ticker_handler())
    await asyncio.gather(stream_task, ticker_loop)

# Start everything
if __name__ == "__main__":
    asyncio.run(main())
