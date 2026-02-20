import duckdb
from pathlib import Path

def initialize_duckdb() -> int:
    DB_PATH = Path(__file__).resolve().parents[1] / "algory.duckdb"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))

    con.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        trade_id BIGINT,
        timestamp TIMESTAMP,
        strategy TEXT,
        symbol TEXT,
        side TEXT,            
        quantity DOUBLE,
        price DOUBLE
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_history (
        timestamp TIMESTAMP,
        total_value DOUBLE,
        total_cash DOUBLE,
        total_positions INT
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS strategy_history (
        timestamp TIMESTAMP,
        strategy TEXT,
        strategy_value DOUBLE,
        cash DOUBLE,
        exposure DOUBLE,
        n_positions INT
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_metrics (
        timestamp TIMESTAMP,

        "PnL" DOUBLE,
        "Absolute PnL" DOUBLE,
        "CAGR" DOUBLE,
        "Max Drawdown" DOUBLE,
        "Sharpe Ratio" DOUBLE,
        "Sortino Ratio" DOUBLE,
        "Volatility" DOUBLE,
        "Value at Risk (95%)" DOUBLE,
        "Beta to Market" DOUBLE,
        "Kurtosis" DOUBLE,
        "Average Trade Return" DOUBLE,
        "Median Trade Return" DOUBLE,
        "Win/Loss Ratio" DOUBLE,
        "Average Win / Average Loss" DOUBLE
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS strategy_metrics (
        timestamp TIMESTAMP,
        strategy TEXT,

        "PnL" DOUBLE,
        "Absolute PnL" DOUBLE,
        "CAGR" DOUBLE,
        "Max Drawdown" DOUBLE,
        "Sharpe Ratio" DOUBLE,
        "Sortino Ratio" DOUBLE,
        "Volatility" DOUBLE,
        "Value at Risk (95%)" DOUBLE,
        "Beta to Market" DOUBLE,
        "Kurtosis" DOUBLE,
        "Average Trade Return" DOUBLE,
        "Median Trade Return" DOUBLE,
        "Win/Loss Ratio" DOUBLE,
        "Average Win / Average Loss" DOUBLE
    );
    """)

    con.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_metrics_ts ON portfolio_metrics (timestamp);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_strategy_metrics_ts ON strategy_metrics (timestamp);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_strategy_metrics_strategy ON strategy_metrics (strategy);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_trades_ts ON trades (timestamp);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_strategy_ts ON strategy_history (timestamp);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_ts ON portfolio_history (timestamp);")

    con.close()
    print(f"DuckDB initialized successfully at '{DB_PATH}'")
    return 100

if __name__ == "__main__":
    initialize_duckdb()