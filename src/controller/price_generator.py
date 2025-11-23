from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

@dataclass
class PriceSnapshot:
    timestamp: datetime
    prices: Dict[str, float]

class PriceGenerator:
    def __init__(
        self,
        tickers: List[str],
        start: datetime | None = None,
        start_range: Tuple[float, float] = (40.0, 500.0),
        drift: float = 0.0001,
        vol: float = 0.01,
        seed: int | None = None
    ) -> None:
        self.tickers = list(tickers)
        self.drift = drift
        self.vol = vol
        if start is None:
            start = datetime.now()
        self.current_time = start
        rng = np.random.default_rng(seed)
        self.rng = rng
        self.prices: Dict[str, float] = {
            t: float(rng.uniform(*start_range)) for t in self.tickers
        }
        self.history: List[PriceSnapshot] = [
            PriceSnapshot(timestamp=self.current_time, prices=dict(self.prices))
        ]
    
    def step(self) -> PriceSnapshot:
        self.current_time = datetime.now()

        for t in self.tickers:
            change = self.rng.normal(self.drift, self.vol)
            self.prices[t] = float(self.prices[t] * (1.0 + change))
        
        snapshot = PriceSnapshot(
            timestamp=self.current_time,
            prices=dict(self.prices),
        )
        self.history.append(snapshot)

        market_level = np.mean(list(self.prices.values()))
        if not hasattr(self, "market_history"):
            self.market_history = []
        self.market_history.append((self.current_time, market_level))
       
        return snapshot
    
    def get_history(self) -> List[PriceSnapshot]:
        return self.history
    
    def get_last(self, n: int):
        return self.history[-n:]
    
