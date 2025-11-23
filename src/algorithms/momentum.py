from .base import BaseAlgorithm, Trade
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import time

from src.controller.price_generator import PriceSnapshot

class Momentum(BaseAlgorithm):
    def __init__(self):
        super().__init__(id="momentum", frequency=2)

        self.lookback: int = 4
        self.upper_threshold: float = 0.01
        self.lower_threshold: float = -0.01

        self.target_dollar: float = 5_000.0
        self.min_trade_dollar: float = 500.0

    def run(self,
            timestamp: datetime,
            prices: Dict[str, float],
            positions: Dict[str, float],
            history: List[PriceSnapshot],
            ) -> Optional[Trade]:
        
        if len(history) <= self.lookback:
            return None
        
        recent = history[-(self.lookback + 1):]

        best_sym: Optional[str] = None
        best_ret: float = 0.0

        for sym in prices.keys():
            try:
                p_old = recent[0].prices[sym]
                p_new = recent[-1].prices[sym]
            except KeyError:
                continue

            if p_old <= 0 or p_new <= 0:
                continue

            r = p_new / p_old - 1.0

            if best_sym is None or r > best_ret:
                best_sym = sym
                best_ret = r
        
        if best_sym is None:
            return None
        
        if best_ret > self.upper_threshold:
            direction = 1.0
        elif best_ret < self.lower_threshold:
            direction = -1.0
        else:
            return None
        
        current_price = prices[best_sym]
        if current_price <= 0 or np.isnan(current_price):
            return None

        target_dollar = self.target_dollar * direction
        target_shares = target_dollar / current_price

        current_shares = positions.get(best_sym, 0.0)
        order_qty = target_shares - current_shares

        if abs(order_qty) * current_price < self.min_trade_dollar:
            return None
        
        ts = timestamp.timestamp()
        trade = Trade(
            strategy_id=self.id,
            timestamp=ts,
            qty=[float(order_qty)],
            symbol=[best_sym],
        )

        self.last_exec = time.time()

        return trade