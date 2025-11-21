import duckdb
import pandas as pd
from typing import Tuple, Any
import numpy as np
import yfinance as yf

# import stats from DuckDB

def get_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    con = duckdb.connect("algory.duckdb")

    portfolio = con.execute("SELECT * FROM portfolio_history ORDER BY timestamp").df()
    strategy = con.execute("SELECT * FROM strategy_history ORDER BY timestamp").df()
    trades = con.execute("SELECT * FROM trades ORDER BY timestamp").df()

    con.close()
    
    return portfolio, strategy, trades

def compute_portfolio_metrics(portfolio_df: pd.DataFrame) -> dict[str, Any]:

    # ---- Copy and sort ----
    df = portfolio_df.sort_values("timestamp").copy()

    # ---- Download benchmark & compute market returns ----
    spy = yf.download("SPY", start="2020-01-01", progress=False, auto_adjust=True)
    spy["returns"] = spy["Close"].pct_change().dropna()
    market_returns = spy["returns"]

    rf_annual = 0.03

    # ---- Compute returns ----
    df["returns"] = df["total_value"].pct_change()
    returns = df["returns"].dropna()

    if returns.empty:
        raise ValueError("Not enough data to compute metrics (need at least 2 rows).")

    # ---- Infer effective periods_per_year ----
    t0 = df["timestamp"].iloc[0]
    t1 = df["timestamp"].iloc[-1]
    years = (t1 - t0).total_seconds() / (365.25 * 24 * 3600)

    if years <= 0:
        years = 1 / 365.25  # guard

    N = len(returns)
    periods_per_year = N / years  # auto-detected frequency

    # ---- Basic PnL ----
    start_val = df["total_value"].iloc[0]
    end_val = df["total_value"].iloc[-1]

    pnl_abs = end_val - start_val
    pnl_pct = end_val / start_val - 1 if start_val > 0 else np.nan

    # ---- CAGR ----
    if start_val > 0:
        cagr = (end_val / start_val) ** (1 / years) - 1
    else:
        cagr = np.nan

    # ---- Max Drawdown ----
    running_max = df["total_value"].cummax()
    drawdown = df["total_value"] / running_max - 1
    max_drawdown = drawdown.min()

    # ---- Sharpe / Vol ----
    rf_per_period = (1 + rf_annual) ** (1 / periods_per_year) - 1
    mean_ret = returns.mean()
    std_ret = returns.std(ddof=1)

    if std_ret != 0:
        sharpe = (mean_ret - rf_per_period) / std_ret * np.sqrt(periods_per_year)
        volatility = std_ret * np.sqrt(periods_per_year)
    else:
        sharpe = np.nan
        volatility = 0.0

    # ---- Sortino ----
    downside = returns[returns < 0]
    if len(downside) > 0:
        downside_dev = np.sqrt((downside ** 2).mean())
        sortino = (mean_ret - rf_per_period) / downside_dev * np.sqrt(periods_per_year)
    else:
        sortino = np.nan

    # ---- VaR ----
    var_95 = np.percentile(returns, 5)

    # ---- Beta ----
    beta = np.nan
    aligned = returns.align(market_returns, join="inner")
    port_r = aligned[0]
    mkt_r  = aligned[1]

    if len(mkt_r) > 1:
        cov = np.cov(port_r, mkt_r)[0, 1]
        var_m = np.var(mkt_r, ddof=1)
        if var_m != 0:
            beta = cov / var_m

    # ---- Kurtosis ----
    kurtosis = returns.kurt()

    # ---- Trade stats ----
    avg_trade_return = returns.mean()
    median_trade_return = returns.median()

    wins = returns[returns > 0]
    losses = returns[returns < 0]

    if len(losses) > 0:
        win_loss_ratio = len(wins) / len(losses)
        avg_win = wins.mean() if len(wins) > 0 else np.nan
        avg_loss = losses.mean()
        avg_win_over_avg_loss = avg_win / abs(avg_loss) if avg_loss != 0 else np.nan
    else:
        win_loss_ratio = np.nan
        avg_win_over_avg_loss = np.nan

    return {
        "PnL": float(pnl_pct),
        "Absolute PnL": float(pnl_abs),
        "CAGR": float(cagr),
        "Max Drawdown": float(max_drawdown),
        "Sharpe Ratio": float(sharpe),
        "Sortino Ratio": float(sortino),
        "Volatility": float(volatility),
        "Value at Risk (95%)": float(var_95),
        "Beta to Market": float(beta),
        "Kurtosis": float(kurtosis),
        "Average Trade Return": float(avg_trade_return),
        "Median Trade Return": float(median_trade_return),
        "Win/Loss Ratio": float(win_loss_ratio),
        "Average Win / Average Loss": float(avg_win_over_avg_loss),
    }

def compute_strategy_metrics(strategy_df: pd.DataFrame) -> dict[str, dict[str, Any]]:

    # ---- Copy ----
    df_all = strategy_df.copy()
    df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])

    # ---- Download benchmark & compute market returns ----
    spy = yf.download("SPY", start="2020-01-01", progress=False, auto_adjust=True)
    spy["returns"] = spy["Close"].pct_change().dropna()
    market_returns = spy["returns"]

    rf_annual = 0.03

    # ---- Initialize results ----
    results: dict[str, dict[str, Any]] = {}

    # ---- Loop over strategies ----
    for strat, df in df_all.groupby("strategy"):
        df = df.sort_values("timestamp").copy()

        # ---- Compute returns ----
        df["returns"] = df["strategy_value"].pct_change()
        returns = df["returns"].dropna()

        if returns.empty:
            results[strat] = {k: np.nan for k in [
                "PnL", "PnL_abs", "CAGR", "Max Drawdown", "Sharpe Ratio",
                "Sortino Ratio", "Volatility", "Value at Risk (95%)",
                "Beta to Market", "Kurtosis", "Average Trade Return",
                "Median Trade Return", "Win/Loss Ratio",
                "Average Win / Average Loss"
            ]}
            continue
            
        # ---- Infer effective periods_per_year ----
        t0 = df["timestamp"].iloc[0]
        t1 = df["timestamp"].iloc[-1]
        years = (t1 - t0).total_seconds() / (365.25 * 24 * 3600)

        if years <= 0:
            years = 1 / 365.25  # guard

        N = len(returns)
        periods_per_year = N / years  # auto-detected frequency

        # ---- Basic PnL ----
        start_val = df["strategy_value"].iloc[0]
        end_val = df["strategy_value"].iloc[-1]

        pnl_abs = end_val - start_val
        pnl_pct = end_val / start_val - 1 if start_val > 0 else np.nan

        # ---- CAGR ----
        if start_val > 0:
            cagr = (end_val / start_val) ** (1 / years) - 1
        else:
            cagr = np.nan

        # ---- Max Drawdown ----
        running_max = df["strategy_value"].cummax()
        drawdown = df["strategy_value"] / running_max - 1
        max_drawdown = drawdown.min()

        # ---- Sharpe / Vol ----
        rf_per_period = (1 + rf_annual) ** (1 / periods_per_year) - 1
        mean_ret = returns.mean()
        std_ret = returns.std(ddof=1)

        if std_ret != 0:
            sharpe = (mean_ret - rf_per_period) / std_ret * np.sqrt(periods_per_year)
            volatility = std_ret * np.sqrt(periods_per_year)
        else:
            sharpe = np.nan
            volatility = 0.0

        # ---- Sortino ----
        downside = returns[returns < 0]
        if len(downside) > 0:
            downside_dev = np.sqrt((downside ** 2).mean())
            sortino = (mean_ret - rf_per_period) / downside_dev * np.sqrt(periods_per_year)
        else:
            sortino = np.nan

        # ---- VaR ----
        var_95 = np.percentile(returns, 5)

        # ---- Beta ----
        beta = np.nan
        aligned = returns.align(market_returns, join="inner")
        port_r = aligned[0]
        mkt_r  = aligned[1]

        if len(mkt_r) > 1:
            cov = np.cov(port_r, mkt_r)[0, 1]
            var_m = np.var(mkt_r, ddof=1)
            if var_m != 0:
                beta = cov / var_m

        # ---- Kurtosis ----
        kurtosis = returns.kurt()

        # ---- Trade-like stats ----
        avg_trade_return = returns.mean()
        median_trade_return = returns.median()

        wins = returns[returns > 0]
        losses = returns[returns < 0]

        if len(losses) > 0:
            win_loss_ratio = len(wins) / len(losses)
            avg_win = wins.mean() if len(wins) > 0 else np.nan
            avg_loss = losses.mean()
            avg_win_over_avg_loss = (
                avg_win / abs(avg_loss) if avg_loss != 0 else np.nan
            )
        else:
            win_loss_ratio = np.nan
            avg_win_over_avg_loss = np.nan

        results[strat] = {
            "PnL": float(pnl_pct),
            "Absolute PnL": float(pnl_abs),
            "CAGR": float(cagr),
            "Max Drawdown": float(max_drawdown),
            "Sharpe Ratio": float(sharpe),
            "Sortino Ratio": float(sortino),
            "Volatility": float(volatility),
            "Value at Risk (95%)": float(var_95),
            "Beta to Market": float(beta),
            "Kurtosis": float(kurtosis),
            "Average Trade Return": float(avg_trade_return),
            "Median Trade Return": float(median_trade_return),
            "Win/Loss Ratio": float(win_loss_ratio),
            "Average Win / Average Loss": float(avg_win_over_avg_loss),
        }
    
    return results