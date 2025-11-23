import duckdb
import numpy as np
import pandas as pd
from datetime import datetime
from ..algorithms.base import Trade


def append_trade(trade: Trade, db_path: str = "algory.duckdb") -> None:
    con = duckdb.connect(db_path)

    timestamp = datetime.fromtimestamp(trade.timestamp)

    legs = [
        (sym, qty, price)
        for sym, qty, price in zip(trade.symbol, trade.qty, trade.price)
        if abs(qty) > 1e-8
    ]
    if not legs:
        con.close()
        return

    for sym, qty, price in legs:

        side = "BUY" if qty > 0 else "SELL"

        con.execute(
            """
            INSERT INTO trades
                (trade_id, timestamp, strategy, symbol, side, quantity, price)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            [trade.trade_id, timestamp, trade.strategy_id, sym, side, float(qty), float(price)]
        )
    con.close()

def append_portfolios(timestamp: datetime, prices: dict[str, float], db_path: str = "algory.duckdb") -> None:
    con = duckdb.connect(db_path)

    df = con.execute("SELECT symbol, quantity, price FROM trades WHERE timestamp <= ? ORDER BY timestamp",[timestamp],).df()
    
    if df.empty:
        con.close()
        return

    grouped = df.groupby(by='symbol').sum(numeric_only=True)
    qty = grouped["quantity"]

    price_series = pd.Series(prices)

    qty_aligned, price_aligned = qty.align(price_series, join="inner")

    positions_value = (qty_aligned * price_aligned).sum()
    total_positions = int((qty_aligned != 0).sum())

    STARTING_CASH = 100_000.0
    cash_flow = (df["quantity"]*df["price"]).sum()
    cash = STARTING_CASH - cash_flow

    portfolio_value = positions_value + cash
    
    con.execute(
        """
        INSERT INTO portfolio_history
            (timestamp, total_value, total_cash, total_positions)
        VALUES (?, ?, ?, ?);
        """,
        [timestamp, float(portfolio_value), float(cash), total_positions],
    )
    con.close()

def append_strategy_portfolios(timestamp: datetime, prices: dict[str, float], db_path: str = "algory.duckdb") -> None:
    con = duckdb.connect(db_path)

    df = con.execute("SELECT strategy, symbol, quantity, price FROM trades WHERE timestamp <= ? ORDER BY timestamp",[timestamp],).df()

    if df.empty:
        con.close()
        return
    
    price_series = pd.Series(prices)
    STARTING_CASH = {
    "momentum": 25_000,
    "mean_reversion": 25_000,
    "pairs": 25_000,
    "cluster_v2": 25_000,
    }

    for strat, strat_df in df.groupby("strategy"):
        

        positions = strat_df.groupby("symbol")["quantity"].sum()
        qty_aligned, price_aligned = positions.align(price_series, join="inner")
        if qty_aligned.empty:
            continue

        positions_value = float((qty_aligned * price_aligned).sum())
        n_positions = int((qty_aligned != 0).sum())

        cash_flow = (strat_df["quantity"] * strat_df["price"]).sum()
        starting_cash = STARTING_CASH[strat]
        cash = starting_cash - cash_flow

        strat_value = positions_value + cash
    
        con.execute(
            """
            INSERT INTO strategy_history
                (timestamp, strategy, strategy_value, cash, exposure, n_positions)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            [timestamp, strat, strat_value, float(cash), positions_value, n_positions],
        )
    con.close()