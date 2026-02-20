"use client";

import { useState } from "react";

type SeriesPoint = { x: string; y: number };

type TradeRow = {
  timestamp: string;
  strategy: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
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

function formatNum(n: number) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
}
function formatMoney(n: number) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
}
function formatPct(n: number) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return (n * 100).toLocaleString(undefined, { maximumFractionDigits: 2 }) + "%";
}

function SidePill({ side }: { side: string }) {
  const s = side?.toLowerCase?.() ?? "";
  const isBuy = s === "buy" || s === "b";
  const isSell = s === "sell" || s === "s";
  return (
    <span
      className={[
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold border",
        isBuy ? "border-green-200 bg-green-50 text-green-700" : "",
        isSell ? "border-red-200 bg-red-50 text-red-700" : "",
        !isBuy && !isSell ? "border-zinc-200 bg-zinc-50 text-zinc-700" : "",
      ].join(" ")}
    >
      {side}
    </span>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-4">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="pt-1 text-base font-semibold text-zinc-900">{value}</div>
    </div>
  );
}

function LineChart({
  data,
  height = 260,
  formatValue,
  formatTick,
}: {
  data: SeriesPoint[];
  height?: number;
  formatValue: (n: number) => string;
  formatTick: (n: number) => string;
}) {
  const w = 1000;
  const h = height;

  const ys = data.map((d) => d.y).filter((v) => Number.isFinite(v));
  const minY = ys.length ? Math.min(...ys) : 0;
  const maxY = ys.length ? Math.max(...ys) : 1;
  const padY = (maxY - minY) * 0.08 || 1;

  const y0 = minY - padY;
  const y1 = maxY + padY;

  const n = data.length;
  const left = 58;
  const right = 18;
  const top = 14;
  const bottom = 34;

  const innerW = w - left - right;
  const innerH = h - top - bottom;

  const sx = (i: number) => (n <= 1 ? left : left + (i / (n - 1)) * innerW);
  const sy = (y: number) => {
    const t = (y - y0) / (y1 - y0);
    return top + (1 - t) * innerH;
  };

  const points = data.map((d, i) => `${sx(i).toFixed(2)},${sy(d.y).toFixed(2)}`).join(" ");

  const last = data.at(-1);
  const lastLabel = last ? formatValue(last.y) : "—";

  const tickCount = 5;
  const ticks = Array.from({ length: tickCount }, (_, i) => {
    const t = i / (tickCount - 1);
    const yVal = y0 + (1 - t) * (y1 - y0);
    const yPix = top + t * innerH;
    return { yVal, yPix };
  });

  const firstX = data.at(0)?.x ?? "";
  const lastX = data.at(-1)?.x ?? "";
  const xLabel = (s: string) => (s ? s.slice(0, 10) : "");

  return (
    <div className="w-full">
      <div className="flex items-baseline justify-between pb-2">
        <div className="text-sm text-zinc-500">{n ? `${n} points` : "No data"}</div>
        <div className="text-sm font-semibold text-zinc-900">{lastLabel}</div>
      </div>

      <div className="w-full overflow-hidden rounded-2xl border border-zinc-200 bg-white">
        <svg viewBox={`0 0 ${w} ${h}`} className="block h-[260px] w-full">
          <rect x={0} y={0} width={w} height={h} fill="white" />

          {ticks.map((t, idx) => (
            <g key={idx}>
              <line x1={left} x2={w - right} y1={t.yPix} y2={t.yPix} className="stroke-zinc-200" />
              <text
                x={left - 10}
                y={t.yPix}
                textAnchor="end"
                dominantBaseline="middle"
                className="fill-zinc-500"
                fontSize="12"
              >
                {formatTick(t.yVal)}
              </text>
            </g>
          ))}

          <line x1={left} x2={left} y1={top} y2={h - bottom} className="stroke-zinc-300" />
          <line x1={left} x2={w - right} y1={h - bottom} y2={h - bottom} className="stroke-zinc-300" />

          <text x={left} y={h - 10} textAnchor="start" className="fill-zinc-500" fontSize="12">
            {xLabel(firstX)}
          </text>
          <text x={w - right} y={h - 10} textAnchor="end" className="fill-zinc-500" fontSize="12">
            {xLabel(lastX)}
          </text>

          <polyline fill="none" stroke="black" strokeWidth={2} points={points} strokeLinejoin="round" strokeLinecap="round" />

          {n ? <circle cx={sx(n - 1)} cy={sy(data[n - 1].y)} r={3.5} fill="black" /> : null}
        </svg>
      </div>
    </div>
  );
}

export default function StrategyClient({
  strategyName,
  series,
  trades,
  metrics,
  description,
}: {
  strategyName: string;
  series: {
    value: SeriesPoint[];
    cash: SeriesPoint[];
    exposure: SeriesPoint[];
    positions: SeriesPoint[];
  };
  trades: TradeRow[];
  metrics: StrategyMetrics | null;
  description: string;
}) {
  const [tab, setTab] = useState<"value" | "cash" | "exposure" | "positions">("value");

  const tabBtn = (key: typeof tab, label: string) => (
    <button
      type="button"
      onClick={() => setTab(key)}
      className={[
        "rounded-full border px-3 py-1.5 text-sm transition",
        tab === key ? "bg-black text-white border-black" : "bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50",
      ].join(" ")}
    >
      {label}
    </button>
  );

  const selected = series[tab];
  const isMoney = tab !== "positions";

  const title = strategyName
    .split("_")
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join(" ");

  return (
    <div className="mx-auto max-w-6xl px-6 py-10 space-y-10">
      {/* Header */}
      <section className="space-y-2">
        <div className="text-xs text-zinc-500">Strategy</div>
        <h1 className="text-2xl tracking-tight">{title}</h1>
      </section>

      {/* Value over time */}
      <section className="space-y-4">
        <h2 className="text-xl tracking-tight">Value over time</h2>

        <div className="rounded-2xl border border-zinc-200 bg-white p-5">
          <div className="flex flex-wrap gap-2 pb-4">
            {tabBtn("value", "Value")}
            {tabBtn("cash", "Cash")}
            {tabBtn("exposure", "Exposure")}
            {tabBtn("positions", "Positions")}
          </div>

          <LineChart
            data={selected}
            formatValue={isMoney ? formatMoney : formatNum}
            formatTick={isMoney ? formatMoney : formatNum}
          />
        </div>
      </section>

      {/* Metrics */}
      <section className="space-y-4">
        <h2 className="text-xl tracking-tight">Metrics</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="PnL" value={metrics?.pnl !== undefined ? formatPct(metrics.pnl) : "—"} />
          <MetricCard label="Absolute PnL" value={metrics?.pnl_abs !== undefined ? formatMoney(metrics.pnl_abs) : "—"} />
          <MetricCard label="CAGR" value={metrics?.cagr !== undefined ? formatPct(metrics.cagr) : "—"} />
          <MetricCard label="Max Drawdown" value={metrics?.max_drawdown !== undefined ? formatPct(metrics.max_drawdown) : "—"} />
          <MetricCard label="Sharpe" value={metrics?.sharpe !== undefined ? formatNum(metrics.sharpe) : "—"} />
          <MetricCard label="Beta" value={metrics?.beta !== undefined ? formatNum(metrics.beta) : "—"} />
          <MetricCard label="Volatility" value={metrics?.volatility !== undefined ? formatPct(metrics.volatility) : "—"} />
          <MetricCard label="VaR (95%)" value={metrics?.var95 !== undefined ? formatPct(metrics.var95) : "—"} />
        </div>
      </section>

      {/* Recent trades */}
      <section className="space-y-4">
        <h2 className="text-xl tracking-tight">Recent trades</h2>

        <div className="rounded-2xl border border-zinc-200 bg-white overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-zinc-50 text-zinc-600">
                <tr className="text-left">
                  <th className="px-4 py-3 font-semibold">Timestamp</th>
                  <th className="px-4 py-3 font-semibold">Ticker</th>
                  <th className="px-4 py-3 font-semibold">Quantity</th>
                  <th className="px-4 py-3 font-semibold">Side</th>
                  <th className="px-4 py-3 font-semibold">Price</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((t, idx) => (
                  <tr key={idx} className="border-t border-zinc-100">
                    <td className="px-4 py-3 whitespace-nowrap text-zinc-700">{t.timestamp}</td>
                    <td className="px-4 py-3 font-semibold">{t.symbol}</td>
                    <td className="px-4 py-3">{formatNum(t.quantity)}</td>
                    <td className="px-4 py-3">
                      <SidePill side={t.side} />
                    </td>
                    <td className="px-4 py-3">{formatMoney(t.price)}</td>
                  </tr>
                ))}
                {!trades.length ? (
                  <tr>
                    <td className="px-4 py-6 text-zinc-500" colSpan={5}>
                      No trades found.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Description */}
      <section className="space-y-3">
        <h2 className="text-xl tracking-tight">Description</h2>
        <div className="rounded-2xl border border-zinc-200 bg-white p-5 text-sm text-zinc-700 leading-relaxed">
          {description}
        </div>
      </section>
    </div>
  );
}