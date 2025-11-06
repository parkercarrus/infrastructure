from alpaca_trade_api.rest import REST
from pathlib import Path
import pandas as pd
import yfinance as yf

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

# Example trade decision for testing makeTrade
trade_decision = pd.DataFrame({
    "QTY": [100, 50, 0],
    "side": ["buy", "sell", "hold"]
}, index=pd.Index(["AAPL", "MSFT", "TSLA"], name="symbol"))

print(trade_decision)

def makeTrade(trade_decision):
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

    pos_path = Path(__file__).parent / "positions.csv"
    pos_df = pd.read_csv(pos_path)
    pos_df["Amount"] = pos_df["Amount"].astype(float)
    holdings = dict(zip(pos_df["Positions"], pos_df["Amount"]))

    for symbol, row in trade_decision.iterrows():
        qty = float(row["QTY"])
        side = row["side"].lower()

        if side == "hold" or qty == 0:
            continue

        price = yf.Ticker(symbol).fast_info.last_price ###### CHANGE THIS !!!!!!!!!

        if symbol not in holdings:
            holdings[symbol] = 0.0
            
        if side == "buy":
            holdings[symbol] += qty
            holdings["CASH"] -= price * qty
        elif side == "sell":
            holdings[symbol] -= qty
            holdings["CASH"] += price * qty
        else:
            continue

    out_df = pd.DataFrame({"Positions": list(holdings.keys()),
                           "Amount":   list(holdings.values())})

    out_df.to_csv(pos_path, index=False)
       
    return order

makeTrade(trade_decision)
