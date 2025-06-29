import requests
import configparser
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# Load from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

api_key = config["keys"]["api_key"]
api_secret = config["keys"]["api_secret"]
base_url = config["urls"]["paper-trading"]  

# Initialize Alpaca Headers
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": api_secret 
}

def get_account():

    url = f"{base_url}/v2/account"

    response = requests.get(url, headers=headers)

    return response.json()["client_order_id"]

def order_stock(payload):

    url = f"{base_url}/v2/orders"

    response = requests.post(url, json=payload, headers=self.headers)

def sell_stock(symbol, qty):

    url = f"{base_url}/v2/orders"
    
    payload = {
        "side": "sell",
        "type": "market",
        "time_in_force": "gtc",
        "symbol": symbol,
        "qty": qty
    }

    response = requests.post(url, json=payload, headers=headers)

def get_bars_data(data_frame, symbol ,time_frame, start_date, feed):
    try:
    
        next_token = None
        
        # While to get all pages with data
        while True:
            # URL for the API request
            url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={time_frame}&start={start_date}&limit=1000&adjustment=raw&feed={feed}&sort=asc"
            if next_token:
                url += f"&page_token={next_token}"
                
            # make request to API
            response = requests.get(url, headers=headers).json()
            df = pd.DataFrame(response["bars"]["TSLA"])
            data_frame = pd.concat([data_frame, df], ignore_index=True)
        

            # If there is no next_token leave loop
            next_token = response['next_page_token']
            if not next_token:
                break

    except:
        print("unexpected error getting bars from API")
    
    return data_frame.drop_duplicates()

def calculate_trade_stats(data_frame):

    total_profit_loss = 0
    profit_loss_values = []
    winning_trades = 0
    value_w = 0
    losing_trades = 0
    value_l = 0
    num_trades = 0

    buy_price = None

    # Iterate through the data_frame and identify BUY/SELL trades
    for index, row in data_frame.iterrows():
        trade_action = row['Trade Action']
        
        # buy action
        if trade_action > 0:
            buy_price = trade_action
        
        # sell action
        elif trade_action < 0:
            sell_price = trade_action * -1
            profit_or_loss = sell_price - buy_price
            

            # Update overall stats
            total_profit_loss += profit_or_loss
            profit_loss_values.append(total_profit_loss)
            if profit_or_loss < 0:  # It's a losing trade
                losing_trades += 1
                value_l += profit_or_loss
            else:  # It's a winning trade
                winning_trades += 1
                value_w += profit_or_loss
            num_trades += 1
            
            # Reset buy price
            buy_price = None

    winning_percentage = (winning_trades / num_trades) * 100 if num_trades > 0 else 0
    loosing_percentage = (losing_trades / num_trades) * 100 if num_trades > 0 else 0
    

    # # Plot the profit/loss over time from the 'profit_loss_values' list
    # plt.plot(profit_loss_values, label="Profit/Loss Over Time", color='green')
    # plt.title('Profit and Loss Over Time')
    # plt.xlabel('Trade Number')
    # plt.ylabel('Profit/Loss')
    # plt.grid(True)
    # plt.legend()
    #
    # # Save the graph as an image file
    # graph_filename = 'profit_loss_graph.png'
    # plt.savefig(graph_filename)

    # Return the final trade statistics
    stats = {
        'total_profit_loss': total_profit_loss,
        'num_trades': num_trades,
        'winning_trades': winning_trades,
        'value_of_winning_trades': value_w,
        'losing_trades': losing_trades,
        'value_of_loosing_trades': value_l,
        'winning_percentage': round(winning_percentage, 2) if num_trades > 0 else 0,
        'loosing_percentage': round(loosing_percentage, 2) if num_trades > 0 else 0
    }
    
    return stats
