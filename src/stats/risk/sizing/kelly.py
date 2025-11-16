from .base import PositionSizer

class KellySizer(PositionSizer):
    def __init__(self, initial_capital, fraction=1.0):
        self.initial_capital = initial_capital
        self.fraction = fraction # Can use half Kelly, etc.

    def get_allocation(self, p=None, R=None, **kwargs):
        if p is None or R is None: 
            return 0.0
        
        f_star = (p * (R + 1) - 1) / R
        f_star = max(0.0, f_star)
        return f_star * self.fraction 