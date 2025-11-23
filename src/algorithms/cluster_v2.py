from .base import BaseAlgorithm, Trade
import numpy as np
import time
from datetime import datetime
from typing import Dict, List
from src.controller.price_generator import PriceSnapshot

class ClusterV2(BaseAlgorithm):
    def __init__(self):
        super().__init__(id="cluster_v2", frequency=4)

    def run(self,
            timestamp: datetime,
            prices: Dict[str, float],
            positions: Dict[str, float],
            history: List[PriceSnapshot],
            ) -> Trade | None:
        
        symbols = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "NVDA", "TSLA", "JPM", "XOM", "KO", "NFLX", "WMT"]
        symbol = [np.random.choice(symbols)]

        if np.random.rand() > 0.2:
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