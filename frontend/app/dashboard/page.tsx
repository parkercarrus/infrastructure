import path from "path";
import duckdb from "duckdb";
import DashboardClient from "./DashboardClient";

export const runtime = "nodejs";

type TradeRow = {
  timestamp: string;
  strategy: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
};

type PortfolioRow = {
  timestamp: string;
  total_value: number;
  total_cash: number;
  total_positions: number;
};

type StrategyRow = {
  timestamp: string;
  strategy: string;
  strategy_value: number;
  cash: number;
  exposure: number;
  n_positions: number;
};

type PortfolioMetrics = {
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

type StrategyMetricsLite = {
  cagr?: number;
  sharpe?: number;
  beta?: number;
};

const STRATEGIES = ["momentum", "mean_reversion", "pairs", "cluster_v2"] as const;

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

    if (params.length) {
      (conn as any).all(sql, params, cb);
    } else {
      (conn as any).all(sql, cb);
    }
  });
}

async function getData() {
  const dbPath = path.join(process.cwd(), "..", "src", "algory.duckdb");

  // Recent trades (global)
  const tradesRaw = await queryAll<any>(
    dbPath,
    `
      SELECT timestamp, strategy, symbol, side, quantity, price
      FROM trades
      ORDER BY timestamp DESC
      LIMIT 12
    `
  );

  const trades: TradeRow[] = tradesRaw.map((r) => ({
    timestamp: normalizeTs(r.timestamp),
    strategy: r.strategy,
    symbol: r.symbol,
    side: r.side,
    quantity: Number(r.quantity),
    price: Number(r.price),
  }));

  // Portfolio history
  const phRaw = await queryAll<any>(
    dbPath,
    `
      SELECT timestamp, total_value, total_cash, total_positions
      FROM portfolio_history
      ORDER BY timestamp ASC
    `
  );

  const portfolio: PortfolioRow[] = phRaw.map((r) => ({
    timestamp: normalizeTs(r.timestamp),
    total_value: Number(r.total_value),
    total_cash: Number(r.total_cash),
    total_positions: Number(r.total_positions),
  }));

  // Strategy history
  const shRaw = await queryAll<any>(
    dbPath,
    `
      SELECT timestamp, strategy, strategy_value, cash, exposure, n_positions
      FROM strategy_history
      ORDER BY strategy, timestamp ASC
    `
  );

  const strategyHistory: StrategyRow[] = shRaw.map((r) => ({
    timestamp: normalizeTs(r.timestamp),
    strategy: r.strategy,
    strategy_value: Number(r.strategy_value),
    cash: Number(r.cash),
    exposure: Number(r.exposure),
    n_positions: Number(r.n_positions),
  }));

  // Trades per strategy
  const tradesByStrategy: Record<string, TradeRow[]> = {};
  for (const s of STRATEGIES) {
    const rows = await queryAll<any>(
      dbPath,
      `
        SELECT timestamp, strategy, symbol, side, quantity, price
        FROM trades
        WHERE strategy = ?
        ORDER BY timestamp DESC
        LIMIT 6
      `,
      [s]
    );

    tradesByStrategy[s] = rows.map((r) => ({
      timestamp: normalizeTs(r.timestamp),
      strategy: r.strategy,
      symbol: r.symbol,
      side: r.side,
      quantity: Number(r.quantity),
      price: Number(r.price),
    }));
  }

  // Latest portfolio metrics (1 row)
  const pmRaw = await queryAll<any>(
    dbPath,
    `
      SELECT *
      FROM portfolio_metrics
      ORDER BY timestamp DESC
      LIMIT 1
    `
  );

  const portfolioMetrics: PortfolioMetrics | null =
    pmRaw.length === 0
      ? null
      : {
          pnl: Number(pmRaw[0]["PnL"]),
          pnl_abs: Number(pmRaw[0]["Absolute PnL"]),
          cagr: Number(pmRaw[0]["CAGR"]),
          max_drawdown: Number(pmRaw[0]["Max Drawdown"]),
          sharpe: Number(pmRaw[0]["Sharpe Ratio"]),
          sortino: Number(pmRaw[0]["Sortino Ratio"]),
          volatility: Number(pmRaw[0]["Volatility"]),
          var95: Number(pmRaw[0]["Value at Risk (95%)"]),
          beta: Number(pmRaw[0]["Beta to Market"]),
          kurtosis: Number(pmRaw[0]["Kurtosis"]),
          avg_trade_return: Number(pmRaw[0]["Average Trade Return"]),
          median_trade_return: Number(pmRaw[0]["Median Trade Return"]),
          win_loss_ratio: Number(pmRaw[0]["Win/Loss Ratio"]),
          avg_win_over_avg_loss: Number(pmRaw[0]["Average Win / Average Loss"]),
        };

  // Latest strategy metrics per strategy
  const smRows = await queryAll<any>(
    dbPath,
    `
      SELECT *
      FROM (
        SELECT
          *,
          ROW_NUMBER() OVER (PARTITION BY strategy ORDER BY timestamp DESC) AS rn
        FROM strategy_metrics
      )
      WHERE rn = 1
    `
  );

  const strategyMetrics: Record<string, StrategyMetricsLite | null> = {};
  for (const s of STRATEGIES) strategyMetrics[s] = null;

  for (const r of smRows) {
    const strat = String(r.strategy);
    strategyMetrics[strat] = {
      cagr: Number(r["CAGR"]),
      sharpe: Number(r["Sharpe Ratio"]),
      beta: Number(r["Beta to Market"]),
    };
  }

  return { trades, portfolio, strategyHistory, tradesByStrategy, portfolioMetrics, strategyMetrics };
}

export default async function DashboardPage() {
  const { trades, portfolio, strategyHistory, tradesByStrategy, portfolioMetrics, strategyMetrics } = await getData();

  const portfolioSeries = {
    value: portfolio.map((r) => ({ x: r.timestamp, y: r.total_value })),
    cash: portfolio.map((r) => ({ x: r.timestamp, y: r.total_cash })),
    exposure: portfolio.map((r) => ({ x: r.timestamp, y: r.total_value - r.total_cash })),
    positions: portfolio.map((r) => ({ x: r.timestamp, y: r.total_positions })),
  };

  return (
    <main className="min-h-screen bg-white text-zinc-900 font-mono">
      <DashboardClient
        trades={trades}
        portfolioSeries={portfolioSeries}
        tradesByStrategy={tradesByStrategy}
        strategyHistory={strategyHistory}
        portfolioMetrics={portfolioMetrics}
        strategyMetrics={strategyMetrics}
      />
    </main>
  );
}