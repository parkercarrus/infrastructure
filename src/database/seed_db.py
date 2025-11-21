# %%
import duckdb

# Connect to the DuckDB database
conn = duckdb.connect('algory.duckdb')

# Get the list of all tables in the database
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()

# Iterate through the tables and delete all rows
for table in tables:
    table_name = table[0]
    conn.execute(f"DELETE FROM {table_name}")

# Close the connection
conn.close()

# %%
import duckdb
import random
import datetime as dt
import numpy as np
from pathlib import Path

def generate_portfolio_history_rows(
    start: dt.datetime,
    periods: int = 500,
    dt_minutes: int = 5,
    start_value: float = 100_000.0,
    cash_ratio_range=(0.05, 0.30),
    pos_range=(5, 25),
    vol=0.002
):
    ts = start
    value = start_value

    for _ in range(periods):
        # GBM-like drift + noise
        drift = 0.0001
        shock = np.random.normal(0, vol)
        value = value * (1 + drift + shock)

        # cash is stable but noisy within bounds
        cash_ratio = random.uniform(*cash_ratio_range)
        total_cash = value * cash_ratio

        # integer positions, random walk within bounds
        positions = random.randint(*pos_range)

        yield {
            "timestamp": ts,
            "total_value": float(value),
            "total_cash": float(total_cash),
            "total_positions": positions,
        }

        ts += dt.timedelta(minutes=dt_minutes)


def insert_seed_portfolio_history():
    DB_PATH = Path(__file__).resolve().parents[1] / "algory.duckdb"
    con = duckdb.connect(str(DB_PATH))

    rows = list(
        generate_portfolio_history_rows(
            start=dt.datetime.now() - dt.timedelta(days=5),
            periods=1000,
            dt_minutes=3,
            start_value=150_000,
            cash_ratio_range=(0.10, 0.35),
            pos_range=(3, 40),
            vol=0.0015,
        )
    )

    # Convert to something DuckDB will accept
    timestamps = [r["timestamp"] for r in rows]
    values = [r["total_value"] for r in rows]
    cashes = [r["total_cash"] for r in rows]
    poss = [r["total_positions"] for r in rows]

    con.execute(
        """
        INSERT INTO portfolio_history (timestamp, total_value, total_cash, total_positions)
        SELECT * FROM (SELECT
            unnest(?::TIMESTAMP[]) AS ts,
            unnest(?::DOUBLE[]) AS tv,
            unnest(?::DOUBLE[]) AS tc,
            unnest(?::INT[]) AS tp
        )
        """,
        [timestamps, values, cashes, poss],
    )

    print(f"Inserted {len(rows)} rows.")


if __name__ == "__main__":
    insert_seed_portfolio_history()

# %%
import duckdb
import random
import datetime as dt
import numpy as np
from pathlib import Path

STRATEGIES = ["momentum", "mean_reversion", "pairs", "cluster_v2"]

def generate_strategy_history_rows(
    start: dt.datetime,
    strategies = STRATEGIES,
    periods: int = 500,
    dt_minutes: int = 5,
    start_value: float = 100_000.0,
    cash_ratio_range=(0.05, 0.30),
    pos_range=(3, 25),
    vol=0.002,
):
    # one independent GBM path per strategy
    values = {
        strat: start_value * (1 + np.random.normal(0, 0.05))  # slight initial dispersion
        for strat in strategies
    }

    ts = start

    for _ in range(periods):
        for strat in strategies:
            # GBM-like update
            drift = 0.0001
            shock = np.random.normal(0, vol)
            values[strat] = values[strat] * (1 + drift + shock)

            strategy_value = float(values[strat])

            # cash as % of value
            cash_ratio = random.uniform(*cash_ratio_range)
            cash = strategy_value * cash_ratio

            # integer positions
            n_positions = random.randint(*pos_range)

            # for now, just set exposure = strategy_value (fully invested, conceptually)
            exposure = strategy_value

            yield {
                "timestamp": ts,
                "strategy": strat,
                "strategy_value": strategy_value,
                "cash": float(cash),
                "exposure": float(exposure),
                "n_positions": n_positions,
            }

        ts += dt.timedelta(minutes=dt_minutes)


def insert_seed_strategy_history():
    DB_PATH = Path(__file__).resolve().parents[1] / "algory.duckdb"
    con = duckdb.connect(str(DB_PATH))

    rows = list(
        generate_strategy_history_rows(
            start=dt.datetime.now() - dt.timedelta(days=5),
            strategies=STRATEGIES,
            periods=500,
            dt_minutes=15,
            start_value=100_000.0,
            cash_ratio_range=(0.10, 0.35),
            pos_range=(3, 40),
            vol=0.0015,
        )
    )

    timestamps = [r["timestamp"] for r in rows]
    strategies = [r["strategy"] for r in rows]
    values = [r["strategy_value"] for r in rows]
    cashes = [r["cash"] for r in rows]
    exposures = [r["exposure"] for r in rows]
    npos = [r["n_positions"] for r in rows]

    con.execute(
        """
        INSERT INTO strategy_history
            (timestamp, strategy, strategy_value, cash, exposure, n_positions)
        SELECT * FROM (
            SELECT
                unnest(?::TIMESTAMP[]) AS ts,
                unnest(?::TEXT[])      AS strategy,
                unnest(?::DOUBLE[])    AS sv,
                unnest(?::DOUBLE[])    AS cash,
                unnest(?::DOUBLE[])    AS exposure,
                unnest(?::INT[])       AS npos
        )
        """,
        [timestamps, strategies, values, cashes, exposures, npos],
    )

    print(f"Inserted {len(rows)} strategy_history rows.")
    con.close()

if __name__ == "__main__":
    insert_seed_strategy_history()



# %%
import duckdb
import random
import datetime as dt
import numpy as np
from pathlib import Path

STRATEGIES = ["momentum", "mean_reversion", "pairs", "cluster_v2"]
SYMBOLS = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "NVDA", "TSLA", "JPM", "XOM", "KO"]


def generate_trades(
    start_time: dt.datetime,
    n: int = 500,
    dt_seconds: int = 90,
    base_prices=None
):
    if base_prices is None:
        base_prices = {s: random.uniform(50, 400) for s in SYMBOLS}

    t = start_time
    trade_id = 1

    for _ in range(n):
        symbol = random.choice(SYMBOLS)
        strategy = random.choice(STRATEGIES)

        # price evolution: small Gaussian noise on base
        price = base_prices[symbol] * (1 + np.random.normal(0, 0.002))
        price = round(price, 2)

        # quantity distribution: small sizes + occasional block trades
        if random.random() < 0.9:
            quantity = round(random.uniform(1, 50), 2)
        else:
            quantity = round(random.uniform(100, 500), 2)

        side = random.choice(["BUY", "SELL"])

        yield {
            "trade_id": trade_id,
            "timestamp": t,
            "strategy": strategy,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }

        trade_id += 1
        t += dt.timedelta(seconds=dt_seconds)


def insert_seed_trades():
    DB_PATH = Path(__file__).resolve().parents[1] / "algory.duckdb"
    con = duckdb.connect(str(DB_PATH))

    rows = list(
        generate_trades(
            start_time=dt.datetime.now() - dt.timedelta(days=5),
            n=1000,
            dt_seconds=45
        )
    )

    trade_id = [r["trade_id"] for r in rows]
    ts = [r["timestamp"] for r in rows]
    strat = [r["strategy"] for r in rows]
    sym = [r["symbol"] for r in rows]
    side = [r["side"] for r in rows]
    qty = [r["quantity"] for r in rows]
    price = [r["price"] for r in rows]

    con.execute(
        """
        INSERT INTO trades (trade_id, timestamp, strategy, symbol, side, quantity, price)
        SELECT * FROM (
            SELECT
                unnest(?::BIGINT[]) AS trade_id,
                unnest(?::TIMESTAMP[]) AS ts,
                unnest(?::TEXT[]) AS strategy,
                unnest(?::TEXT[]) AS symbol,
                unnest(?::TEXT[]) AS side,
                unnest(?::DOUBLE[]) AS quantity,
                unnest(?::DOUBLE[]) AS price
        );
        """,
        [trade_id, ts, strat, sym, side, qty, price],
    )

    print(f"Inserted {len(rows)} trades.")


if __name__ == "__main__":
    insert_seed_trades()


# %%
