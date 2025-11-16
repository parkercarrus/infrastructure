from algorithms.base import BaseAlgorithm, Trade
import numpy as np
import time

class DummyTest(BaseAlgorithm):
    id = "DummyStrat"
    frequency = 2

    def run(self):
        """Return a random buy/sell decision for one of aapl, tsla, nvda, msft."""
        symbols = ["AAPL", "TSLA", "NVDA", "MSFT"]
        symbol = [np.random.choice(symbols)]
        if np.random.rand() > 0.7:
            qty = [np.random.normal(0, 2)]
        else:
            qty = [0]

        trade = Trade(self.id, time.time(), qty, symbol)
        self.last_exec = time.time()

        return trade