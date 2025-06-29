import requests

def fetch_account_cash(headers):
    url = "https://demo.trading212.com/api/v0/equity/account/cash"

    response = requests.get(url, headers=headers)

    return response.json()
