import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime

def addReturns():
    base = Path(__file__).parent
    pos_path = base / "positions.csv"
    ret_path = base / "returns.csv"

    pos_df = pd.read_csv(pos_path)
    pos_df["Positions"] = pos_df["Positions"].astype(str)
    pos_df["Amount"] = pd.to_numeric(pos_df["Amount"], errors="coerce").fillna(0.0)

    cash = float(pos_df.loc[pos_df["Positions"] == "CASH", "Amount"].sum())
    positions = pos_df[pos_df["Positions"] != "CASH"]

    total_positions_value = 0.0
    for _, row in positions.iterrows():
        sym = row["Positions"]
        shares = float(row["Amount"])
        if shares == 0:
            continue
        price = yf.Ticker(sym).fast_info.last_price
        total_positions_value += shares * price

    total_value = cash + total_positions_value

    row = pd.DataFrame([{
        "Date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "Value": float(total_value)
    }])

    header = not ret_path.exists()
    row.to_csv(ret_path, mode="a", index=False, header=header)

    print(f"Logged: {row.iloc[0]['Date']}  Value={total_value:,.2f} -> {ret_path}")

addReturns()

def stats():
    ret_path = Path(__file__).parent / "returns.csv"
    df = pd.read_csv(ret_path, parse_dates=["Date"])
    df.sort_values("Date")

    df["Return"] = df["Value"].pct_change()

    days = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days
    years = days / 365.25
    cagr = (df["Value"].iloc[-1] / df["Value"].iloc[0]) ** (1/years) - 1

    sharpe = (df["Return"].mean() / df["Return"].std()) * np.sqrt(252)

    start = df["Date"].iloc[0]
    end = df["Date"].iloc[-1]
    benchmark = yf.download("^SP500TR", start=start, end=end)["Close"].pct_change()
    combined = pd.concat([df["Return"], benchmark], axis=1)
    combined.columns = ["Portfolio", "Benchmark"]
    combined = combined.dropna()
    cov = np.cov(combined["Portfolio"], combined["Benchmark"])[0][1]
    var = np.var(combined["Benchmark"])
    beta = cov / var

    print("\n📊 Portfolio Performance Stats")
    print("--------------------------------")
    print(f"CAGR:            {cagr*100:.2f}%")
    print(f"Sharpe Ratio:     {sharpe:.2f}")
    print(f"Beta vs S&P 500:  {beta:.2f}")
    print(f"Days of Data:     {len(combined)}")

    return cagr, sharpe, beta

stats()




