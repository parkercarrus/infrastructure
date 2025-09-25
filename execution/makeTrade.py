from alpaca_trade_api.rest import REST, TimeFrame

API_KEY = "PKYTZ90KAKSJZPMHF3GF"
API_SECRET = "j4hgcUDxg5qkexthRYGKY7yuTm1y21ih44YUdQRa"
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(API_KEY, API_SECRET, BASE_URL)

account = api.get_account()
print(f"Account Status: {account.status}")
print(f"Buying Power: ${account.buying_power}")

# Place a paper trade
symbol = "AAPL"  # Stock symbol
qty = 1  # Quantity to buy
side = "buy"  # Buy or sell
order_type = "market"  # Order type
time_in_force = "gtc"  # Good 'til canceled

try:
    order = api.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,
        type=order_type,
        time_in_force=time_in_force
    )
    print(f"Order submitted: {order}")
except Exception as e:
    print(f"Error placing order: {e}")