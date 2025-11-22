from .base import BaseAlgorithm, Trade
import numpy as np
import time

class MeanReversion(BaseAlgorithm):
    def __init__(self):
        super().__init__(id="mean_reversion", frequency=2)

    def run(self) -> Trade:
        symbols = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "NVDA", "TSLA", "JPM", "XOM", "KO", "NFLX", "WMT"]
        symbol = [np.random.choice(symbols)]

        if np.random.rand() > 0.7:
            size = abs(np.random.normal(0, 2)) 
            if size < 0.01:
                return None  
            qty = [size]
        else:
            return None
    
        now = time.time()
        trade = Trade(self.id, now, qty, symbol)

        self.last_exec = now

        return trade
