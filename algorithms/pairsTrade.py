from typing import List, Dict, Any
import pandas as pd

from algorithms.base import BaseAlgorithm

try:
    import yfinance as yf
except Exception:
    yf = None

class PairsTradingAlgo(BaseAlgorithm):
    name = "pairs_trading"
    version = "1.0.0"

    def __init__(self, strategy: Dict[str, Any], logger=None, stop_evt=None) -> None:
        super().__init__(strategy, logger, stop_evt)

    def run(self, context: Dict[str, Any]) -> pd.DataFrame:
        params = self.merged_params(
            defaults={"tickers": ["AAPL", "MSFT"], "days": 30, "lot": 100},
            context=context,
        )
        tickers: List[str] = params["tickers"]
        days: int = int(params["days"])
        lot: int = int(params["lot"])

        if yf is None:
            return self._hold_df(tickers)
        return self.latest_decisions(tickers, days, lot)

    # Core logic
    def get_daily_prices(self, ticker: str, days: int) -> pd.DataFrame:
        """
        Fetch daily prices for the past `days` using Yahoo Finance.
        Returns a DataFrame with columns ['timestamp', 'close'] (UTC time).
        """
        if yf is None:
            return pd.DataFrame(columns=["timestamp", "close"])

        lookback_days = max(1, int(days) + 5)
        try:
            hist = yf.Ticker(ticker).history(period=f"{lookback_days}d", interval="1d", auto_adjust=False)
        except Exception:
            hist = pd.DataFrame()

        if hist is None or hist.empty:
            self.logger.warning(f"[{ticker}] no data from Yahoo Finance")
            return pd.DataFrame(columns=["timestamp", "close"])

        # Prefer 'Close', fall back to 'Adj Close'
        if "Close" in hist.columns:
            s = hist["Close"]
        elif "Adj Close" in hist.columns:
            s = hist["Adj Close"]
        else:
            self.logger.warning(f"[{ticker}] no Close/Adj Close in columns: {list(hist.columns)}")
            return pd.DataFrame(columns=["timestamp", "close"])

        # Convert to DataFrame with standard schema
        out = s.to_frame(name="close").reset_index()

        # Normalize timestamp column name and type
        if "Date" in out.columns:
            out.rename(columns={"Date": "timestamp"}, inplace=True)
        elif "Datetime" in out.columns:
            out.rename(columns={"Datetime": "timestamp"}, inplace=True)
        elif out.columns[0] != "timestamp":
            out.rename(columns={out.columns[0]: "timestamp"}, inplace=True)

        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
        out = out.dropna(subset=["timestamp", "close"])

        # Keep last `days` calendar days
        end_date = pd.Timestamp.now(tz="UTC").normalize()
        cutoff = end_date - pd.Timedelta(days=days)
        out = out[out["timestamp"] >= cutoff].sort_values("timestamp")
        return out[["timestamp", "close"]]

    def pairs_trading_strategy(self, tickers: List[str], days: int = 30) -> pd.DataFrame:
        if len(tickers) != 2:
            raise ValueError("tickers must be exactly two symbols, e.g. ['AAPL','MSFT']")
        t0, t1 = tickers
        p0 = self.get_daily_prices(t0, days).rename(columns={"close": f"close_{t0}"})
        p1 = self.get_daily_prices(t1, days).rename(columns={"close": f"close_{t1}"})
        if p0.empty or p1.empty:
            return pd.DataFrame(columns=["timestamp", "signal"])

        df = p0.merge(p1, on="timestamp", how="inner")
        if df.empty:
            return pd.DataFrame(columns=["timestamp", "signal"])

        # Z-score normalization for each stock price series
        for t in tickers:
            col = f"close_{t}"
            std = df[col].std()
            df[col] = (df[col] - df[col].mean()) / (std if std and std != 0 else 1.0)

        df["spread"] = df[f"close_{t0}"] - df[f"close_{t1}"]
        mu = df["spread"].mean()
        sd = df["spread"].std() or 1.0

        df["signal"] = 0
        df.loc[df["spread"] > mu + sd, "signal"] = -1  # Short t0, Long t1
        df.loc[df["spread"] < mu - sd, "signal"] = 1  # Long t0, Short t1
        return df

    def latest_decisions(self, tickers: List[str], days: int, lot: int) -> pd.DataFrame:
        t0, t1 = tickers
        hist = self.pairs_trading_strategy(tickers, days)
        if hist.empty:
            return self._hold_df(tickers)

        sig = int(hist.iloc[-1]["signal"])
        if sig == 1:
            actions = {t0: ("BUY", lot), t1: ("SELL", lot)}
        elif sig == -1:
            actions = {t0: ("SELL", lot), t1: ("BUY", lot)}
        else:
            actions = {t0: ("HOLD", 0), t1: ("HOLD", 0)}

        out = pd.DataFrame.from_dict(
            {sym: {"QTY": qty, "side": side} for sym, (side, qty) in actions.items()},
            orient="index",
        )
        out.index.name = "symbol"
        return out

    @staticmethod
    def _hold_df(tickers: List[str]) -> pd.DataFrame:
        return pd.DataFrame(
            {"QTY": [0] * len(tickers), "side": ["HOLD"] * len(tickers)},
            index=pd.Index(tickers, name="symbol"),
        )
