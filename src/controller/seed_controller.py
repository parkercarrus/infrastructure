import time
import duckdb
import numpy as np
from pathlib import Path
from typing import Tuple

from src.algorithms.base import BaseAlgorithm, Trade
from src.algorithms.momentum import Momentum
from src.algorithms.mean_reversion import MeanReversion
from src.algorithms.pairs import Pairs
from src.algorithms.cluster_v2 import ClusterV2

from src.controller.price_generator import PriceGenerator

from src.database.append import (
    append_trade,
    append_portfolios,
    append_strategy_portfolios,
)

TICKERS = ["AAPL", "MSFT", "AMZN", "GOOG", "META",
           "NVDA", "TSLA", "JPM", "XOM", "KO", "NFLX", "WMT"]

DB_PATH = str(Path(__file__).resolve().parents[1] / "algory.duckdb")

BOOKKEEP_INTERVAL = 2

def call_positions(db_path: str) -> dict[str, dict[str,float]]:
    con = duckdb.connect(db_path)

    df = con.execute(
        """
        SELECT strategy, symbol, SUM(quantity) AS qty
        FROM trades
        GROUP BY strategy, symbol;
        """).df()
    con.close()

    grouped = {}
    for strat, group in df.groupby("strategy"):
        grouped[strat] = dict(zip(group.symbol, group.qty))

    return grouped

def startup() -> Tuple[dict[str, BaseAlgorithm], PriceGenerator]:

    cluster_v2 = ClusterV2()
    mean_reversion = MeanReversion()
    momentum = Momentum()
    pairs = Pairs()

    strategy_dict: dict[str, BaseAlgorithm] = {
        cluster_v2.id: cluster_v2,
        mean_reversion.id: mean_reversion,
        momentum.id: momentum,
        pairs.id: pairs,
    }

    price_gen = PriceGenerator(
        tickers=TICKERS,
        start_range=(40.0,500.0),
        seed=67
    )

    con = duckdb.connect(DB_PATH)
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    ).fetchall()
    for (name,) in tables:
        con.execute(f"DELETE FROM {name}")
    con.close()

    return strategy_dict, price_gen

def trigger_trade(strategy: BaseAlgorithm) -> bool:
    now = time.time()
    if now - strategy.last_exec >= strategy.frequency:
        return True
    return False

last_bookkeep = 0
def trigger_bookkeep() -> bool:
    global last_bookkeep
    now = time.time()
    if now - last_bookkeep >= BOOKKEEP_INTERVAL:
        last_bookkeep = now
        return True
    return False


def main_loop(strategy_dict: dict[str, BaseAlgorithm], price_gen: PriceGenerator, db_path:str = DB_PATH) -> None:
    snapshot = price_gen.step()
    now = snapshot.timestamp
    prices = snapshot.prices
    history = price_gen.get_last(20)
    positions = call_positions(db_path)
    
    for strategy in strategy_dict.values():

        if trigger_trade(strategy):
            strat_positions = positions.get(strategy.id, {})
            trade_decision: Trade = strategy.run(timestamp=now,prices=prices,positions=strat_positions,history=history)

            if trade_decision is None:
                continue
            if not getattr(trade_decision, "qty", None):
                continue
            if max(abs(q) for q in trade_decision.qty) < 1e-6:
                continue

            trade_decision.price = [
                    float(prices.get(sym, float("nan"))) for sym in trade_decision.symbol
                ]
            

            '''
            # When its time to sync with alpaca
            try:
                make_trade(trade_decision)
            except Exception as e:
                print(f"[WARNING] Failed to send trade to Alpaca: {e}")
            '''
            
            append_trade(trade_decision, db_path=db_path)
            strategy.last_exec = time.time()

    if trigger_bookkeep():
        append_portfolios(timestamp=now, prices=prices, db_path=db_path)
        append_strategy_portfolios(timestamp=now, prices=prices, db_path=db_path)

def main() -> None:
    print("Controller Started.")
    print(f"Using DB at: {DB_PATH}")
    strategies, price_gen = startup()
    print(f"Initialized {len(strategies)} strategies, initialized price generator, and cleared DB.")

    for i in range(200):
        main_loop(strategies, price_gen, DB_PATH)
        time.sleep(0.1)
        if (i) % 20 == 0:
            print(f"{(i)//2}% Complete")
    print("Completed run of seed controller. Trades and bookkeeps updated in DB. View data and stats in 'read_db.ipynb'.")

if __name__ == "__main__":
    main()
    





