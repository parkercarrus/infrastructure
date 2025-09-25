from alpaca_trade_api.rest import REST
from strategies.pairsTrade import runStrategy

API_KEY = "PKYTZ90KAKSJZPMHF3GF"
API_SECRET = "j4hgcUDxg5qkexthRYGKY7yuTm1y21ih44YUdQRa"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)

account = api.get_account()
print(f"Account Status: {account.status}")
print(f"Buying Power: ${account.buying_power}")

ctx = {
            "params": {"tickers": ["AAPL", "MSFT"], "days": 30, "lot": 200},
            "secrets": {"polygon": "mZTD9O_UchKeLHg1cN1iybKJhIKvwxBL"}
        }
trade_decision = runStrategy(ctx)

def makeTrade(trade_decision): # camelCase
    order = {}
    for symbol, row in trade_decision.iterrows():
        qty = row["QTY"]
        side = row["side"]
        if side == "hold" or qty == 0:
            continue 
        order[symbol] = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )
    return order

print(makeTrade(trade_decision))

