from typing import List, Optional

class Trade:
    def __init__(self, strategy_id: str, timestamp: float, qty: List[float], symbol: List[str], price: Optional[List[float]] = None, trade_id: int | None=None,):
        self.strategy_id =  strategy_id
        self.timestamp = timestamp
        self.qty = qty
        self.symbol = symbol

        if price is None:
            self.price = [float('nan')] * len(symbol)
        else:
            self.price = price
        
        if trade_id is None:
            self.trade_id = int(timestamp * 1_000_000)   # microsecond-based
        else:
            self.trade_id = trade_id

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

    def run(self) -> Trade:
        raise NotImplementedError("Algorithm must implement run()")