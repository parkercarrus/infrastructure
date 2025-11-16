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
    
    return
