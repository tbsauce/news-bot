import sys
import time
from utils import * 

import requests
import configparser
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from alpaca.trading.client import TradingClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.historical.corporate_actions import CorporateActionsClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.trading.stream import TradingStream
from alpaca.data.live.stock import StockDataStream

from alpaca.data.requests import * 
from alpaca.trading.requests import * 
from alpaca.trading.enums import *

# Load from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

api_key = config["keys"]["api_key"]
secret_key = config["keys"]["api_secret"]
paper=True

stock_historical_data_client = StockHistoricalDataClient(api_key, secret_key)
trade_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=paper)
stock_data_stream_client = StockDataStream(api_key, secret_key)

def main():

    symbol = "TSLA"
    timeframe = TimeFrame(amount = 1, unit = TimeFrameUnit.Hour)
    feed="iex"
    days = 1 

    data_request = StockBarsRequest(
        symbol_or_symbols = [symbol],
        timeframe=TimeFrame(amount = 1, unit = TimeFrameUnit.Minute), 
        start = (datetime.now() - timedelta(days=days)).date(),  
        feed=feed,
    )

    data_frame = stock_historical_data_client.get_stock_bars(data_request).df
    close_price = data_frame.iloc[-1]["close"]

    qty = math.floor((close_price / get_account()["cash"]) * 10) / 10
    entry_price = close_price * 1.1
    take_profit = close_price * 2
    stop_loss = close_price * 1

    req = StopLimitOrderRequest(
                symbol = symbol,
                qty = qty,
                side = OrderSide.BUY,
                time_in_force = TimeInForce.DAY,
                stop_price = entry_price, 
                order_class = OrderClass.BRACKET,
                take_profit = TakeProfitRequest(limit_price=take_profit),
                stop_loss = StopLossRequest(stop_price=stop_loss)
    )
    res = trade_client.submit_order(req)

if __name__ == "__main__":
    main()
