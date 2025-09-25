# strategies/pairs_trading.py
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import pandas as pd


try:
    from polygon import RESTClient
except Exception:
    RESTClient = None  # allow import without polygon installed


class PairsTrading:
    def __init__(self, api_key: str):
        if RESTClient is None:
            raise RuntimeError("polygon package not installed. `pip install polygon-api-client`")
        self.client = RESTClient(api_key)

    def getDailyPrices(self, ticker: str, days: int) -> pd.DataFrame:
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
        } for bar in bars]  # polygon returns iterable of AggregateBars
        df = pd.DataFrame(data).sort_values("timestamp")
        return df

    def pairsTradingStrategy(self, tickers: List[str], days: int = 30) -> pd.DataFrame:
        if len(tickers) != 2:
            raise ValueError("tickers must be exactly two symbols, e.g., ['AAPL','MSFT']")
        t0, t1 = tickers

        # fetch and standardize closes
        p0 = self.getDailyPrices(t0, days).rename(columns={"close": f"close_{t0}"})
        p1 = self.getDailyPrices(t1, days).rename(columns={"close": f"close_{t1}"})

        df = p0.merge(p1, on="timestamp", how="inner")
        for t in tickers:
            col = f"close_{t}"
            std = df[col].std()
            # guard against zero variance
            df[col] = (df[col] - df[col].mean()) / (std if std and std != 0 else 1.0)

        # spread and signal
        df["spread"] = df[f"close_{t0}"] - df[f"close_{t1}"]
        mu, sd = df["spread"].mean(), df["spread"].std() or 1.0

        df["signal"] = 0
        df.loc[df["spread"] > mu + sd, "signal"] = -1   # Short t0, Long t1
        df.loc[df["spread"] < mu - sd, "signal"] =  1   # Long t0, Short t1
        return df

    def latestDecisions(self, tickers: List[str], days: int, lot: int) -> pd.DataFrame:
        t0, t1 = tickers
        hist = self.pairsTradingStrategy(tickers, days)
        if hist.empty:
            return pd.DataFrame(columns=["QTY", "side"], index=pd.Index(tickers, name="symbol"))

        sig = int(hist.iloc[-1]["signal"])
        # Map signal to per-symbol action
        if sig == 1:
            actions = {t0: ("buy", lot),  t1: ("sell", lot)}
        elif sig == -1:
            actions = {t0: ("sell", lot), t1: ("buy", lot)}
        else:
            actions = {t0: ("hold", 0),   t1: ("hold", 0)}

        df = pd.DataFrame.from_dict(
            {sym: {"QTY": qty, "side": side} for sym, (side, qty) in actions.items()},
            orient="index"
        )
        df.index.name = "symbol"
        return df


def resolveParameters(ctx: Dict[str, Any]) -> Dict[str, Any]:
    params = (ctx.get("params") or {})
    tickers = params.get("tickers", ["AAPL", "MSFT"])
    days = int(params.get("days", 30))
    lot = int(params.get("lot", 100))
    return {"tickers": tickers, "days": days, "lot": lot}


def resolveAPIKey(ctx: Dict[str, Any]) -> Optional[str]:
    return os.getenv("POLYGON_API_KEY") or (ctx.get("secrets") or {}).get("polygon")


def runStrategy(ctx: Dict[str, Any]) -> pd.DataFrame:
    """
    Controller entrypoint. Returns a DataFrame indexed by symbol with columns: QTY, side.
    - ctx['params'] may include: {'tickers': [...], 'days': 30, 'lot': 100}
    - polygon API key comes from POLYGON_API_KEY env var or ctx['secrets']['polygon']
    """
    params = resolveParameters(ctx)
    api_key = resolveAPIKey(ctx)

    # Fail-safe: if no key, return HOLD zeros
    if not api_key or RESTClient is None:
        tickers = params["tickers"]
        return pd.DataFrame(
            {"QTY": [0]*len(tickers), "side": ["hold"]*len(tickers)},
            index=pd.Index(tickers, name="symbol")
        )

    strat = PairsTrading(api_key)
    return strat.latestDecisions(params["tickers"], params["days"], params["lot"])
