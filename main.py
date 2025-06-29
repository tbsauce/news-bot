from webscraper import *
import math

def main():

    #TODO
    # Make the stop loss ajust with time going up

    symbol = "TSLA"
    timeframe = "1min"
    feed="iex"
    start_date = (datetime.now() - timedelta(days=1)).date()

    data_frame = pd.DataFrame()
    data_frame = get_bars_data(data_frame, symbol, timeframe, start_date, feed)
    close_price = data_frame.iloc[-1]["c"]

    qty = math.floor((close_price / get_account()["cash"]) * 10) / 10
    entry_price = close_price * 1.1
    take_profit = close_price * 2
    stop_loss = close_price * 1

    #Order payload
    payload = {
        "symbol": symbol,
        "qty": str(qty),
        "side": "buy",
        "type": "stop_limit",
        "time_in_force": "gtc",
        "stop_price": str(entry_price),     
        "order_class": "bracket",
        "take_profit": {
            "limit_price": str(take_profit) 
        },
        "stop_loss": {
            "stop_price": str(stop_loss),
        }
    }

    order_stock(payload)

if __name__ == "__main__":
    main()
