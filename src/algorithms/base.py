from typing import List, Dict
from datetime import datetime
from src.controller.price_generator import PriceSnapshot

class Trade:
    def __init__(self, strategy_id: str, timestamp: float, qty: List[float], symbol: List[str], price: List[float] | None = None, trade_id: int | None=None):
        self.strategy_id =  strategy_id
        self.timestamp = float(timestamp)
        self.qty = qty
        self.symbol = symbol
        self.price = price or [float("nan")] * len(symbol)
        self.trade_id = trade_id or int(timestamp * 1_000_000)
        

    def __str__(self) -> str:
        return (
            f"Trade(strategy_id={self.strategy_id!r}, "
            f"timestamp={self.timestamp}, "
            f"qty={self.qty}, symbol={self.symbol}, "
            f"price={self.price}, trade_id={self.trade_id})"
        )
        
class BaseAlgorithm:
    def __init__(self, id: str, frequency: int):
        self.id = id
        self.frequency = frequency
        self.last_exec = 0.0

    def run(
            self,
            timestamp: datetime,
            prices: Dict[str, float],
            positions: Dict[str, float],
            history: List[PriceSnapshot]
    ) -> Trade:
        raise NotImplementedError("Algorithm must implement run()")