import time
from typing import List

class Trade:
    def __init__(self, strategy_id: str, timestamp: float, qty: List[float], symbol: List[str]):
        self.strategy_id =  strategy_id
        self.timestamp = timestamp
        self.qty = qty
        self.symbol = symbol

    def __str__(self) -> None:
        return(f"Trade(strategy_id={self.strategy_id!r}, timestamp={self.timestamp}, qty={self.qty}, symbol={self.symbol})")
        
class BaseAlgorithm:
    def __init__(self, id: str, frequency: int):
        self.id = id
        self.frequency: int
        self.last_exec: float = 0

    def run() -> Trade:
        return Trade