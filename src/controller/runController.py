import time
from algorithms.base import Trade, BaseAlgorithm
from algorithms import dummyTest
import numpy as np
from database import init_duckdb, append

def startup() -> tuple[dict[str, BaseAlgorithm], dict[str, int]]:

    # Initialize Strategy Tracking
    dummy_strategy = dummyTest.DummyTest('dummy_strategy', 1)
    strategy_dict = { "dummy_strategy": dummy_strategy }
    strategy_frequencies = {strategy.id: strategy.frequency for strategy in strategy_dict.values()}

    return strategy_dict, strategy_frequencies

def execute(trade: Trade) -> int:
    return 100

def is_strategy_time(id: str, strategy: BaseAlgorithm) -> bool:
    if abs(time.time() % strategy.frequency) < 1 and (time.time() - strategy.last_exec > 1):
        return True
    else:
        return False

def is_bookkeeping_time() -> bool:
    if np.random.rand() > 0.95: 
        return True
    else:
        return False

def main_loop(strategy_dict: dict[str, BaseAlgorithm], strategy_frequencies: dict[str: int]):

    for strategy in strategy_dict.values():
        if is_strategy_time(strategy, strategy):
            trade_decision = strategy.run() # current trade decision
            print(trade_decision)
            res = execute(trade_decision)

            if abs(max(trade_decision.qty)) > 0:
                append.append_trade(trade_decision)
    if is_bookkeeping_time():        
        append.append_portfolios()



def main():
    strategy_dict, strategy_frequencies = startup()
    for i in range(10000):
        main_loop(strategy_dict, strategy_frequencies)
        time.sleep(0.01)

main()