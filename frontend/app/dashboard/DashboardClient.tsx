"use client";

import { useMemo, useState } from "react";

type SeriesPoint = { x: string; y: number };
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

const STRATEGIES = ["momentum", "mean_reversion", "pairs", "cluster_v2"] as const;

function formatNum(n: number) {
  if (Number.isNaN(n) || n === null || n === undefined) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
}
function formatMoney(n: number) {
  if (Number.isNaN(n) || n === null || n === undefined) return "—";
  return n.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
}

function LineChart({
  data,
  height = 260,
  formatValue,
  formatTick,
}: {
  data: SeriesPoint[];
  height?: number;
  formatValue: (n: number) => string;   // used for “Latest: …”
  formatTick: (n: number) => string;    // used for axis labels
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
  const left = 58; // wider for y labels
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

  // ticks
  const tickCount = 5;
  const ticks = Array.from({ length: tickCount }, (_, i) => {
    const t = i / (tickCount - 1); // 0..1
    const yVal = y0 + (1 - t) * (y1 - y0); // top tick is y1
    const yPix = top + t * innerH;
    return { yVal, yPix };
  });

  const firstX = data.at(0)?.x ?? "";
  const lastX = data.at(-1)?.x ?? "";
  const xLabel = (s: string) => (s ? s.slice(0, 10) : ""); // YYYY-MM-DD

  return (
    <div className="w-full">
      <div className="flex items-baseline justify-between pb-2">
        <div className="text-sm text-zinc-500">{n ? `${n} points` : "No data"}</div>
        <div className="text-sm font-semibold text-zinc-900">{lastLabel}</div>
      </div>

      <div className="w-full overflow-hidden rounded-2xl border border-zinc-200 bg-white">
        <svg viewBox={`0 0 ${w} ${h}`} className="block h-[260px] w-full">
          <rect x={0} y={0} width={w} height={h} fill="white" />

          {/* horizontal grid + y ticks */}
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

          {/* axes */}
          <line x1={left} x2={left} y1={top} y2={h - bottom} className="stroke-zinc-300" />
          <line x1={left} x2={w - right} y1={h - bottom} y2={h - bottom} className="stroke-zinc-300" />

          {/* x labels (first/last) */}
          <text x={left} y={h - 10} textAnchor="start" className="fill-zinc-500" fontSize="12">
            {xLabel(firstX)}
          </text>
          <text x={w - right} y={h - 10} textAnchor="end" className="fill-zinc-500" fontSize="12">
            {xLabel(lastX)}
          </text>

          {/* line */}
          <polyline
            fill="none"
            stroke="black"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
            points={points}
          />

          {/* endpoint dot */}
          {n ? <circle cx={sx(n - 1)} cy={sy(data[n - 1].y)} r={3.5} fill="black" /> : null}
        </svg>
      </div>
    </div>
  );
}

function Sparkline({ data }: { data: number[] }) {
  const w = 220;
  const h = 140;
  const pad = 6;
  const ys = data.filter((v) => Number.isFinite(v));
  const min = ys.length ? Math.min(...ys) : 0;
  const max = ys.length ? Math.max(...ys) : 1;
  const span = max - min || 1;

  const n = data.length;
  const pts = data
    .map((y, i) => {
      const x = pad + (n <= 1 ? 0 : (i / (n - 1)) * (w - pad * 2));
      const t = (y - min) / span;
      const yy = pad + (1 - t) * (h - pad * 2);
      return `${x.toFixed(2)},${yy.toFixed(2)}`;
    })
    .join(" ");

  return (
    <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
      <svg viewBox={`0 0 ${w} ${h}`} className="block h-[300px] w-full">
        <rect x={0} y={0} width={w} height={h} fill="white" />
        <polyline fill="none" stroke="black" strokeWidth={2} points={pts} strokeLinejoin="round" strokeLinecap="round" />
      </svg>
    </div>
  );
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

export default function DashboardClient({
  trades,
  portfolioSeries,
  tradesByStrategy,
  strategyHistory,
}: {
  trades: TradeRow[];
  portfolioSeries: {
    value: SeriesPoint[];
    cash: SeriesPoint[];
    exposure: SeriesPoint[];
    positions: SeriesPoint[];
  };
  tradesByStrategy: Record<string, TradeRow[]>;
  strategyHistory: StrategyRow[];
}) {
  const [tab, setTab] = useState<"value" | "cash" | "exposure" | "positions">("value");

  const historyByStrategy = useMemo(() => {
    const m: Record<string, StrategyRow[]> = {};
    for (const s of STRATEGIES) m[s] = [];
    for (const r of strategyHistory) {
      if (m[r.strategy]) m[r.strategy].push(r);
    }
    return m;
  }, [strategyHistory]);

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

  const series = portfolioSeries[tab];
  const isMoney = tab !== "positions";

  return (
    <div className="mx-auto max-w-6xl px-6 py-10 space-y-10">
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
            data={series}
            formatValue={isMoney ? formatMoney : formatNum}
            formatTick={isMoney ? formatMoney : formatNum}
            />
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
                  <th className="px-4 py-3 font-semibold">Strategy</th>
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
                    <td className="px-4 py-3">{t.strategy}</td>
                  </tr>
                ))}
                {!trades.length ? (
                  <tr>
                    <td className="px-4 py-6 text-zinc-500" colSpan={6}>
                      No trades found.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Strategies */}
      <section className="space-y-4">
        <h2 className="text-xl tracking-tight">Strategies</h2>

        <div className="grid grid-cols-1 gap-6">
          {STRATEGIES.map((s) => {
            const rows = historyByStrategy[s] ?? [];
            const spark = rows.slice(-60).map((r) => r.strategy_value);
            const recent = tradesByStrategy[s] ?? [];

            const title = s
              .split("_")
              .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
              .join(" ");

            return (
              <a
                key={s}
                href={`/dashboard/strategy/${s}`}
                className="block rounded-2xl border border-zinc-200 bg-white p-5 hover:border-zinc-300 hover:shadow-sm transition"
              >
                <div className="flex flex-col lg:flex-row gap-5 lg:items-start lg:justify-between">
                  <div className="flex-1">
                    <div className="flex items-baseline justify-between">
                      <h3 className="text-lg font-semibold">{title}</h3>
                      <span className="text-xs text-zinc-500 underline">Open</span>
                    </div>

                    <div className="mt-3 rounded-xl border border-zinc-200 overflow-hidden">
                      <div className="bg-zinc-50 px-3 py-2 text-xs font-semibold text-zinc-600">
                        Recent trades
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full text-xs">
                          <thead className="text-zinc-500">
                            <tr className="text-left border-t border-zinc-100">
                              <th className="px-3 py-2 font-semibold">Timestamp</th>
                              <th className="px-3 py-2 font-semibold">Ticker</th>
                              <th className="px-3 py-2 font-semibold">Qty</th>
                              <th className="px-3 py-2 font-semibold">Side</th>
                              <th className="px-3 py-2 font-semibold">Price</th>
                            </tr>
                          </thead>
                          <tbody>
                            {recent.map((t, i) => (
                              <tr key={i} className="border-t border-zinc-100">
                                <td className="px-3 py-2 whitespace-nowrap text-zinc-700">{t.timestamp}</td>
                                <td className="px-3 py-2 font-semibold">{t.symbol}</td>
                                <td className="px-3 py-2">{formatNum(t.quantity)}</td>
                                <td className="px-3 py-2">
                                  <SidePill side={t.side} />
                                </td>
                                <td className="px-3 py-2">{formatMoney(t.price)}</td>
                              </tr>
                            ))}
                            {!recent.length ? (
                              <tr>
                                <td className="px-3 py-4 text-zinc-500" colSpan={5}>
                                  No trades for this strategy.
                                </td>
                              </tr>
                            ) : null}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="w-full lg:w-[360px]">
                    <div className="text-xs text-zinc-500 pb-2">Strategy value</div>
                    <Sparkline data={spark.length ? spark : [0, 0, 0, 0]} />
                    <div className="pt-2 text-xs text-zinc-500">
                      Latest:{" "}
                      <span className="font-semibold text-zinc-900">
                        {rows.length ? formatMoney(rows.at(-1)!.strategy_value) : "—"}
                      </span>
                    </div>
                  </div>
                </div>
              </a>
            );
          })}
        </div>
      </section>
    </div>
  );
}