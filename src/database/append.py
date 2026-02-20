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

def append_portfolio_metrics(
    timestamp: datetime,
    metrics: dict[str, float],
    db_path: str = "algory.duckdb",
) -> None:
    """
    metrics is the dict returned by compute_portfolio_metrics()
    """
    con = duckdb.connect(db_path)
    try:
        con.execute(
            """
            INSERT INTO portfolio_metrics (
                timestamp,
                "PnL",
                "Absolute PnL",
                "CAGR",
                "Max Drawdown",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Volatility",
                "Value at Risk (95%)",
                "Beta to Market",
                "Kurtosis",
                "Average Trade Return",
                "Median Trade Return",
                "Win/Loss Ratio",
                "Average Win / Average Loss"
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                timestamp,
                float(metrics.get("PnL", np.nan)),
                float(metrics.get("Absolute PnL", np.nan)),
                float(metrics.get("CAGR", np.nan)),
                float(metrics.get("Max Drawdown", np.nan)),
                float(metrics.get("Sharpe Ratio", np.nan)),
                float(metrics.get("Sortino Ratio", np.nan)),
                float(metrics.get("Volatility", np.nan)),
                float(metrics.get("Value at Risk (95%)", np.nan)),
                float(metrics.get("Beta to Market", np.nan)),
                float(metrics.get("Kurtosis", np.nan)),
                float(metrics.get("Average Trade Return", np.nan)),
                float(metrics.get("Median Trade Return", np.nan)),
                float(metrics.get("Win/Loss Ratio", np.nan)),
                float(metrics.get("Average Win / Average Loss", np.nan)),
            ],
        )
    finally:
        con.close()


def append_strategy_metrics(
    timestamp: datetime,
    metrics_by_strategy: dict[str, dict[str, float]],
    db_path: str = "algory.duckdb",
) -> None:
    """
    metrics_by_strategy is the dict returned by compute_strategy_metrics()
    """
    con = duckdb.connect(db_path)
    try:
        for strategy, m in metrics_by_strategy.items():
            con.execute(
                """
                INSERT INTO strategy_metrics (
                    timestamp,
                    strategy,
                    "PnL",
                    "Absolute PnL",
                    "CAGR",
                    "Max Drawdown",
                    "Sharpe Ratio",
                    "Sortino Ratio",
                    "Volatility",
                    "Value at Risk (95%)",
                    "Beta to Market",
                    "Kurtosis",
                    "Average Trade Return",
                    "Median Trade Return",
                    "Win/Loss Ratio",
                    "Average Win / Average Loss"
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                [
                    timestamp,
                    strategy,
                    float(m.get("PnL", np.nan)),
                    float(m.get("Absolute PnL", np.nan)),
                    float(m.get("CAGR", np.nan)),
                    float(m.get("Max Drawdown", np.nan)),
                    float(m.get("Sharpe Ratio", np.nan)),
                    float(m.get("Sortino Ratio", np.nan)),
                    float(m.get("Volatility", np.nan)),
                    float(m.get("Value at Risk (95%)", np.nan)),
                    float(m.get("Beta to Market", np.nan)),
                    float(m.get("Kurtosis", np.nan)),
                    float(m.get("Average Trade Return", np.nan)),
                    float(m.get("Median Trade Return", np.nan)),
                    float(m.get("Win/Loss Ratio", np.nan)),
                    float(m.get("Average Win / Average Loss", np.nan)),
                ],
            )
    finally:
        con.close()