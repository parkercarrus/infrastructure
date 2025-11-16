import duckdb
import pandas as pd
from typing import Tuple, Any

# import stats from DuckDB

def get_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    con = duckdb.connect("algory.duckdb")

    portfolio = con.execute("SELECT * FROM portfolio_history ORDER BY timestamp").df()
    trades = con.execute("SELECT * FROM trades ORDER BY timestamp").df()

    con.close()
    
    return portfolio, trades

def compute_portfolio_metrics(portfolio_df: pd.DataFrame) -> dict[str: Any]:
    need_to_do_something_with_var = portfolio_df
    return {
        "sharpe": 1.2,
        "cagr": 24.1,
        "max_drawdown": 10
    }
