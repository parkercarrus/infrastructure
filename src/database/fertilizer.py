import duckdb
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from ..algorithms.base import Trade
from ..algorithms.cluster_v2 import ClusterV2
from ..algorithms.mean_reversion import MeanReversion
from ..algorithms.momentum import Momentum
from ..algorithms.pairs import Pairs

from .append import append_trade, append_portfolios, append_strategy_portfolios

TICKERS = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "NVDA", "TSLA", "JPM", "XOM", "KO", "NFLX", "WMT"]
STRATEGIES = [ClusterV2(), MeanReversion(), Momentum(), Pairs()]
price_map: Dict[datetime, Dict[str, float]] = {}


def build_price_map(hours: int = 1000, tickers = TICKERS, start_range = (50.0, 400.0)):
    end = datetime.now()

    timestamps = [end - timedelta(hours=h) for h in range(hours, 0, -1)]

    prices = {t: np.random.uniform(*start_range) for t in tickers}
    
    out: Dict[datetime, Dict[str, float]] = {}
    
    for ts in timestamps:
        step: Dict[str, float] = {}

        for t in tickers:
            change = np.random.normal(0.0001, 0.01)
            prices[t] = prices[t] * (1.0 + change)
            step[t] = float(prices[t])
        out[ts] = step

    return out

def call_algorithms(timestamp: datetime, prices: Dict[str, float]) -> List[Trade]:
    trades: List[Trade] = []

    for strat in STRATEGIES:
        trade = strat.run()
        if trade is None:
            continue

        if not getattr(trade, "strategy_id", None):
            trade.strategy_id = getattr(strat, "id", strat.__class__.__name__)
        
        trade.timestamp = timestamp.timestamp()

        if not isinstance(trade.symbol, list):
            trade.symbol = [trade.symbol]
        if not isinstance(trade.qty, list):
            trade.qty = [trade.qty]
        trade.price = [float(prices[sym]) for sym in trade.symbol]
    
        trades.append(trade)

    return trades

def clear_all_tables(db_path: str) -> None:
    con = duckdb.connect(db_path)
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    ).fetchall()
    for (name,) in tables:
        con.execute(f"DELETE FROM {name}")
    con.close()

def fertilize(hours: int = 200):
    global price_map

    DB_PATH = str(Path(__file__).resolve().parents[1] / "algory.duckdb")

    clear_all_tables(DB_PATH)

    price_map = build_price_map(hours=hours, tickers=TICKERS)

    for ts in sorted(price_map.keys()):
        prices = price_map[ts]

        trades = call_algorithms(ts, prices)

        for trade in trades:
            trade.price = [prices[sym] for sym in trade.symbol]
            append_trade(trade, db_path=DB_PATH)
        
        append_portfolios(timestamp=ts, prices=prices, db_path=DB_PATH)
        append_strategy_portfolios(timestamp=ts, prices=prices, db_path=DB_PATH)
    
    print("Fertilized.")

if __name__ == "__main__":
    fertilize()