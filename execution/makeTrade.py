from alpaca_trade_api.rest import REST

API_KEY = "api_key"
API_SECRET = "api_key"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)

def make_trade(symbol, qty, side, order_type, time_in_force):
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force
        )
        return order
    except Exception as e:
        return f"Error placing order: {e}"
