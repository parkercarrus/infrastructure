import duckdb
import numpy as np
import pandas as pd
from typing import List
from datetime import datetime
from algorithms.base import Trade


def append_trade(trade: Trade, db_path: str = "algory.duckdb") -> None:
    con = duckdb.connect(db_path)

    # Unpack Trade
    strategy = trade.strategy_id
    timestamp = datetime.fromtimestamp(trade.timestamp)

    for sym, qty in zip(trade.symbol, trade.qty):
        side = "BUY" if qty > 0 else "SELL"
        price = 100
        trade_id = int(timestamp.timestamp() * 1e6)

        con.execute(
            """
            INSERT INTO trades
                (trade_id, timestamp, strategy, symbol, side, quantity, price)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            [trade_id, timestamp, strategy, sym, side, float(qty), price]
        )
    df = con.execute("SELECT * FROM trades LIMIT 5").df()
    con.close()

def append_portfolios(db_path: str = "algory.duckdb") -> None:
    con = duckdb.connect(db_path)

    df = con.execute("SELECT * FROM trades ORDER BY timestamp").df()
    grouped = df.groupby(by='symbol').sum(numeric_only=True)

    random_prices = pd.Series(np.random.uniform(90, 110, size=len(grouped)), index=grouped.index)
    portfolio_value = (grouped.quantity * random_prices).sum()
    
    con.execute(
        """
        INSERT INTO portfolio_history
            (timestamp, total_value, total_cash, total_positions)
        VALUES (?, ?, ?, ?);
        """,
        [datetime.now(), portfolio_value, 100, len(grouped)]
    )
    con.close()