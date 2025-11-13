from typing import List, Dict, Any
import duckdb
import json

conn = duckdb.connect('algory.duckdb')

def store_trades(
    strategy_id: str,
    ts_str: str,
    trades: List[Dict[str, Any]],
):
    """
    Expects trades as list of dicts with at least:
        symbol, side, qty, price   (keys can be adapted below)
    Stores to trade_history in Algory.duckdb.
    """
    if not trades:
        return
    
    rows = []
    for t in trades:
        symbol = (
            t.get("symbol")
            or t.get("asset")
            or t.get("ticker")
        )
        side = t.get("side")
        qty_raw = t.get("qty") or t.get("quantity") or 0
        price_raw = t.get("price") or 0

        try:
            qty = float(qty_raw)
        except Exception:
            qty = 0.0
        try:
            price = float(price_raw)
        except Exception:
            price = 0.0

        notional = float(t.get("notional") or qty * price)

        rows.append(
            (
                ts_str,
                strategy_id,
                symbol,
                side,
                qty,
                price,
                notional,
                json.dumps(t),
            )
        )

    conn.executemany(
        """
        INSERT INTO trade_history
            (ts, strategy_id, symbol, side, qty, price, notional, raw)
        VALUES (?,  ?,          ?,      ?,    ?,   ?,     ?,        ?)
        """,
        rows,
    )