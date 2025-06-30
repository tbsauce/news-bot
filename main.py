import sys
import math
import time
import configparser
from datetime import datetime, timedelta, timezone
from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import *
from alpaca.trading.requests import *
from alpaca.trading.enums import *

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")
api_key = config["keys"]["api_key"]
secret_key = config["keys"]["api_secret"]
paper = True

def main():
    # Initialize clients
    stock_client = StockHistoricalDataClient(api_key, secret_key)
    trade_client = TradingClient(api_key, secret_key, paper=paper)
    symbol = "TSLA"
    
    while True:
        try:
            # Get latest bar
            latest_bar = stock_client.get_stock_latest_bar(StockLatestBarRequest(symbol_or_symbols=symbol))
            bar_data = latest_bar[symbol]
            
            # Calculate position
            close_price = bar_data.close
            account = trade_client.get_account()
            buying_power = account.non_marginable_buying_power
            risk_percentage = 0.10
            risk_amount = float(buying_power) * risk_percentage

            qty = round(risk_amount / close_price, 2)
            stop_price = close_price * 1.1
            limit_price = close_price * 1.11
            take_profit = close_price * 2
            stop_loss = close_price * 0.9
            
            print("\n" + "═"*50)
            print(f"  {symbol} TRADE SIGNAL - {bar_data.timestamp.strftime('%Y-%m-%d %H:%M UTC')}")
            print("═"*50)
            print(f"  ⎣ Current Price: ${close_price:.2f}")
            print(f"  ⎣ Available Cash: ${float(buying_power):,.2f}")
            print(f"  ⎣ Risk Amount (10%): ${risk_amount:,.2f}")
            print(f"  ⎣ Quantity: {qty:.2f} shares")
            print("─"*50)
            print(f"  ⎣ Entry: ${close_price * 1.1:.2f} (+10%)")
            print(f"  ⎣ Take Profit: ${close_price * 2:.2f} (+100%)")
            print(f"  ⎣ Stop Loss: ${close_price * 0.9:.2f} (-10%)")
            print("═"*50)
            
            req = StopLimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                stop_price=stop_price,
                limit_price=limit_price,
                order_class=OrderClass.BRACKET,
                take_profit=TakeProfitRequest(limit_price=take_profit),
                stop_loss=StopLossRequest(stop_price=stop_loss)
            )
            # trade_client.submit_order(req)
            
            # Sleep until next minute + 30 seconds (to get fresh data)
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Script stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            time.sleep(10)  # Wait before retrying

if __name__ == "__main__":
    main()
