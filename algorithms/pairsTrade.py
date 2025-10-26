from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from algorithms.base import BaseAlgorithm


class PairsTradingAlgo(BaseAlgorithm):

    name = "pairs_trading"
    version = "1.0.0"

    def __init__(self, strategy: Dict[str, Any], logger=None, stop_evt=None) -> None:
        super().__init__(strategy, logger, stop_evt)
        self.client = None

    # --- core API ------------------------------------------------------------
    def run(self, context: Dict[str, Any]) -> pd.DataFrame:
        params = self.merged_params(
            defaults={"tickers": ["AAPL", "MSFT"], "days": 30, "lot": 100},
            context=context,
        )
        tickers: List[str] = params["tickers"]
        days: int = int(params["days"])
        lot: int = int(params["lot"])

        # Resolve API key and dependency
        api_key = self.env_or_secret("POLYGON_API_KEY", "polygon", context=context)

        # Fail-safe: return HOLD zeros if no key or dependency missing
        RESTClient = self._maybe_rest_client()
        if not api_key or RESTClient is None:
            return self._hold_df(tickers)

        # Lazy client
        if self.client is None:
            self.client = RESTClient(api_key)

        # Compute latest decisions
        return self.latest_decisions(tickers, days, lot)

    # --- computation ---------------------------------------------------------
    def get_daily_prices(self, ticker: str, days: int) -> pd.DataFrame:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        bars = self.client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=start_date.strftime("%Y-%m-%d"),
            to=end_date.strftime("%Y-%m-%d"),
        )
        data = [{
            "timestamp": pd.to_datetime(bar.timestamp, unit="ms", utc=True),
            "close": float(bar.close)
        } for bar in bars]
        df = pd.DataFrame(data).sort_values("timestamp")
        return df

    def pairs_trading_strategy(self, tickers: List[str], days: int = 30) -> pd.DataFrame:
        if len(tickers) != 2:
            raise ValueError("tickers must be exactly two symbols, e.g., ['AAPL','MSFT']")
        t0, t1 = tickers

        # fetch and standardize closes
        p0 = self.get_daily_prices(t0, days).rename(columns={"close": f"close_{t0}"})
        p1 = self.get_daily_prices(t1, days).rename(columns={"close": f"close_{t1}"})

        df = p0.merge(p1, on="timestamp", how="inner")
        for t in tickers:
            col = f"close_{t}"
            std = df[col].std()
            df[col] = (df[col] - df[col].mean()) / (std if std and std != 0 else 1.0)

        # spread and signal
        df["spread"] = df[f"close_{t0}"] - df[f"close_{t1}"]
        mu, sd = df["spread"].mean(), df["spread"].std() or 1.0

        df["signal"] = 0
        df.loc[df["spread"] > mu + sd, "signal"] = -1   # Short t0, Long t1
        df.loc[df["spread"] < mu - sd, "signal"] =  1   # Long t0, Short t1
        return df

    def latest_decisions(self, tickers: List[str], days: int, lot: int) -> pd.DataFrame:
        t0, t1 = tickers
        hist = self.pairs_trading_strategy(tickers, days)
        if hist.empty:
            return self._hold_df(tickers)

        sig = int(hist.iloc[-1]["signal"])
        if sig == 1:
            actions = {t0: ("BUY", lot),  t1: ("SELL", lot)}
        elif sig == -1:
            actions = {t0: ("SELL", lot), t1: ("BUY", lot)}
        else:
            actions = {t0: ("HOLD", 0),   t1: ("HOLD", 0)}

        df = pd.DataFrame.from_dict(
            {sym: {"QTY": qty, "side": side} for sym, (side, qty) in actions.items()},
            orient="index"
        )
        df.index.name = "symbol"
        return df

    # --- helpers -------------------------------------------------------------
    def _maybe_rest_client(self):
        """
        Try to import polygon.RESTClient; return None if unavailable.
        """
        try:
            polygon_mod = self.require_import("polygon", "pip install polygon-api-client")
            return getattr(polygon_mod, "RESTClient")
        except Exception:
            return None

    @staticmethod
    def _hold_df(tickers: List[str]) -> pd.DataFrame:
        return pd.DataFrame(
            {"QTY": [0]*len(tickers), "side": ["HOLD"]*len(tickers)},
            index=pd.Index(tickers, name="symbol")
        )
