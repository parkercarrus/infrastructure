import path from "path";
import duckdb from "duckdb";
import StrategyClient from "./StrategyClient";

export const runtime = "nodejs";

type TradeRow = {
  timestamp: string;
  strategy: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
};

type StrategyRow = {
  timestamp: string;
  strategy: string;
  strategy_value: number;
  cash: number;
  exposure: number;
  n_positions: number;
};

type StrategyMetrics = {
  pnl?: number;
  pnl_abs?: number;
  cagr?: number;
  max_drawdown?: number;
  sharpe?: number;
  sortino?: number;
  volatility?: number;
  var95?: number;
  beta?: number;
  kurtosis?: number;
  avg_trade_return?: number;
  median_trade_return?: number;
  win_loss_ratio?: number;
  avg_win_over_avg_loss?: number;
};

function normalizeTs(x: any) {
  if (!x) return "";
  if (x instanceof Date) return x.toISOString();
  return String(x);
}

async function queryAll<T>(dbPath: string, sql: string, params: any[] = []): Promise<T[]> {
  const db = new duckdb.Database(dbPath);
  const conn = db.connect();

  return await new Promise<T[]>((resolve, reject) => {
    const cb = (err: any, rows: T[]) => {
      try {
        conn.close();
      } catch {}
      if (err) reject(err);
      else resolve(rows);
    };

    if (params.length) (conn as any).all(sql, params, cb);
    else (conn as any).all(sql, cb);
  });
}

async function getData() {
  const dbPath = path.join(process.cwd(), "..", "src", "algory.duckdb");
  const STRATEGY = "mean_reversion";

  const histRaw = await queryAll<any>(
    dbPath,
    `
      SELECT timestamp, strategy, strategy_value, cash, exposure, n_positions
      FROM strategy_history
      WHERE strategy = ?
      ORDER BY timestamp ASC
    `,
    [STRATEGY]
  );

  const history: StrategyRow[] = histRaw.map((r) => ({
    timestamp: normalizeTs(r.timestamp),
    strategy: r.strategy,
    strategy_value: Number(r.strategy_value),
    cash: Number(r.cash),
    exposure: Number(r.exposure),
    n_positions: Number(r.n_positions),
  }));

  const tradesRaw = await queryAll<any>(
    dbPath,
    `
      SELECT timestamp, strategy, symbol, side, quantity, price
      FROM trades
      WHERE strategy = ?
      ORDER BY timestamp DESC
      LIMIT 12
    `,
    [STRATEGY]
  );

  const trades: TradeRow[] = tradesRaw.map((r) => ({
    timestamp: normalizeTs(r.timestamp),
    strategy: r.strategy,
    symbol: r.symbol,
    side: r.side,
    quantity: Number(r.quantity),
    price: Number(r.price),
  }));

  const metricsRaw = await queryAll<any>(
    dbPath,
    `
      SELECT *
      FROM strategy_metrics
      WHERE strategy = ?
      ORDER BY timestamp DESC
      LIMIT 1
    `,
    [STRATEGY]
  );

  const metrics: StrategyMetrics | null =
    metricsRaw.length === 0
      ? null
      : {
          pnl: Number(metricsRaw[0]["PnL"]),
          pnl_abs: Number(metricsRaw[0]["Absolute PnL"]),
          cagr: Number(metricsRaw[0]["CAGR"]),
          max_drawdown: Number(metricsRaw[0]["Max Drawdown"]),
          sharpe: Number(metricsRaw[0]["Sharpe Ratio"]),
          sortino: Number(metricsRaw[0]["Sortino Ratio"]),
          volatility: Number(metricsRaw[0]["Volatility"]),
          var95: Number(metricsRaw[0]["Value at Risk (95%)"]),
          beta: Number(metricsRaw[0]["Beta to Market"]),
          kurtosis: Number(metricsRaw[0]["Kurtosis"]),
          avg_trade_return: Number(metricsRaw[0]["Average Trade Return"]),
          median_trade_return: Number(metricsRaw[0]["Median Trade Return"]),
          win_loss_ratio: Number(metricsRaw[0]["Win/Loss Ratio"]),
          avg_win_over_avg_loss: Number(metricsRaw[0]["Average Win / Average Loss"]),
        };

  const series = {
    value: history.map((r) => ({ x: r.timestamp, y: r.strategy_value })),
    cash: history.map((r) => ({ x: r.timestamp, y: r.cash })),
    exposure: history.map((r) => ({ x: r.timestamp, y: r.exposure })),
    positions: history.map((r) => ({ x: r.timestamp, y: r.n_positions })),
  };

  return { series, trades, metrics, strategyName: STRATEGY };
}

export default async function MeanReversionStrategyPage() {
  const { series, trades, metrics, strategyName } = await getData();

  return (
    <main className="min-h-screen bg-white text-zinc-900 font-mono">
      <StrategyClient
        strategyName={strategyName}
        series={series}
        trades={trades}
        metrics={metrics}
        description={"The mean reversion strategy identifies assets that have deviated significantly from their recent average price and trades on the expectation that they will revert toward that mean. Using a 10-period lookback window, it computes a moving average for each asset and measures the percentage deviation of the current price from that average. If a price falls more than 1% below its moving average, the strategy enters a long position; if it rises more than 1% above the average, it enters a short position. Positions are adjusted in fixed increments of 5 shares, with an enforced maximum exposure of 100 shares per asset to control risk. By systematically buying relative weakness and selling relative strength, the strategy seeks to profit from short-term price dislocations while maintaining disciplined position limits."}
      />
    </main>
  );
}