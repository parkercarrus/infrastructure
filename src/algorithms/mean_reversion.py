from .base import BaseAlgorithm, Trade
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import time

from src.controller.price_generator import PriceSnapshot

class MeanReversion(BaseAlgorithm):
    def __init__(self):
        super().__init__(id="mean_reversion", frequency=2)

        self.lookback = 10
        self.z_entry = 0.01
        self.base_trade_qty = 5.0
        self.max_position = 100.0

    def run(self,
            timestamp: datetime,
            prices: Dict[str, float],
            positions: Dict[str, float],
            history: List[PriceSnapshot],
            ) -> Optional[Trade]:
        
        if len(history) < self.lookback:
            return None
        
        recent = history[-self.lookback :]

        ma: Dict[str, float] = {}
        for sym in prices.keys():
            series = [snap.prices.get(sym) for snap in recent if sym in snap.prices]
            if not series:
                continue
            ma[sym] = float(np.mean(series))

        deviations: Dict[str, float] = {}
        for sym, px in prices.items():
            m = ma.get(sym)
            if m is None or m == 0.0:
                continue
            dev = (px - m) / m
            deviations[sym] = dev
        
        directions: Dict[str, int] = {}
        for sym, dev in deviations.items():
            if dev < -self.z_entry:
                directions[sym] = +1
            elif dev > self.z_entry:
                directions[sym] = -1
        
        if not directions:
            return None
        
        symbols: List[str] = []
        qtys: List[float] = []

        for sym, direction in directions.items():
            if direction == 0:
                continue

            current_pos = float(positions.get(sym, 0.0))

            raw_order = direction * self.base_trade_qty

            if direction > 0:
                max_buy = self.max_position - current_pos
                order_qty = min(raw_order, max_buy)
            else:
                max_sell = -self.max_position - current_pos
                order_qty = max(raw_order, max_sell)
            
            if abs(order_qty) < 1e-3:
                continue

            symbols.append(sym)
            qtys.append(order_qty)
        
        if not symbols:
            return None
        
        ts = timestamp.timestamp()
        trade = Trade(
            strategy_id = self.id,
            timestamp = ts,
            qty=qtys,
            symbol=symbols,
        )
        return trade