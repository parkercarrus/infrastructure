from alpaca_trade_api.rest import REST
from ..algorithms.base import Trade

API_KEY = "api_key"
API_SECRET = "api_key"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)

account = api.get_account()
print(f"Account Status: {account.status}")
print(f"Buying Power: ${account.buying_power}")

def make_trade(trade: Trade):
    orders = {}
    for sym, qty in zip(trade.symbol, trade.qty):
        if abs(qty) < 1e-6:
               continue
        side = "buy" if qty > 0 else "sell"
        qty_abs = abs(qty)
        
        print(f"Submitting Order: {side.upper()} {qty_abs} {sym}")
        
        order = api.submit_order(
            symbol=sym,
            qty=qty_abs,
            side=side,
            type='market',
            time_in_force='gtc'
        )
        orders[sym] = order
    return order


