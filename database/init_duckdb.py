import duckdb
from pathlib import Path

def initialize_duckdb(db_path: str = "algory.duckdb"):
    """
    Initializes the DuckDB database schema
    """

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(db_path)

    con.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        trade_id BIGINT,
        timestamp TIMESTAMP,
        strategy TEXT,
        symbol TEXT,
        side TEXT,            
        quantity DOUBLE,
        price DOUBLE,
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_history (
        timestamp TIMESTAMP,
        total_value DOUBLE,
        total_cash DOUBLE,
        total_positions INT,
        exposure DOUBLE
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS strategy_history (
        timestamp TIMESTAMP,
        strategy TEXT,
        strategy_value DOUBLE,
        cash DOUBLE,
        exposure DOUBLE,
        n_positions INT,
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_metrics (
        timestamp TIMESTAMP,
        strategy TEXT,
        sharpe DOUBLE,
        sortino DOUBLE,
        drawdown DOUBLE,
        volatility DOUBLE,
        win_rate DOUBLE
    );
    """)

    con.execute("CREATE INDEX IF NOT EXISTS idx_trades_ts ON trades (timestamp);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_strategy_ts ON strategy_history (timestamp);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_ts ON portfolio_history (timestamp);")

    con.close()
    print(f"DuckDB initialized successfully at '{db_path}'")
