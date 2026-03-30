"use client";

import { useMemo, useState } from "react";
import type { Position } from "./page";

type SortKey = "ticker" | "entryDate" | "avgCost" | "numShares" | "costBasis" | "weight" | "daysHeld";
type SortDir = "asc" | "desc";

function formatMoney(n: number) {
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
}

function formatPct(n: number, decimals = 1) {
  if (!Number.isFinite(n)) return "—";
  return (n * 100).toFixed(decimals) + "%";
}

function formatNum(n: number) {
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

/** Horizontal allocation bar for a single position */
function AllocationBar({
  ticker,
  weight,
  costBasis,
  maxWeight,
}: {
  ticker: string;
  weight: number;
  costBasis: number;
  maxWeight: number;
}) {
  const pct = maxWeight > 0 ? (weight / maxWeight) * 100 : 0;
  return (
    <div className="flex items-center gap-3 py-1.5">
      <div className="w-14 text-xs font-semibold text-zinc-900 text-right shrink-0">
        {ticker}
      </div>
      <div className="flex-1 h-5 rounded-full bg-zinc-100 overflow-hidden">
        <div
          className="h-full rounded-full bg-zinc-900 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="w-16 text-xs text-zinc-600 text-right shrink-0">
        {formatPct(weight)}
      </div>
      <div className="w-24 text-xs text-zinc-500 text-right shrink-0">
        {formatMoney(costBasis)}
      </div>
    </div>
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

function SortButton({
  col,
  label,
  sortKey,
  sortDir,
  onSort,
}: {
  col: SortKey;
  label: string;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
}) {
  const active = col === sortKey;
  return (
    <th
      className="px-4 py-3 font-semibold cursor-pointer select-none whitespace-nowrap"
      onClick={() => onSort(col)}
    >
      <span className="flex items-center gap-1">
        {label}
        <span className="text-zinc-400 text-[10px]">
          {active ? (sortDir === "asc" ? "▲" : "▼") : "⇅"}
        </span>
      </span>
    </th>
  );
}

export default function PortfolioClient({
  positions,
  totalInvested,
  avgPositionSize,
  largestPosition,
}: {
  positions: Position[];
  totalInvested: number;
  avgPositionSize: number;
  largestPosition: Position | null;
}) {
  const [sortKey, setSortKey] = useState<SortKey>("costBasis");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [tab, setTab] = useState<"table" | "allocation">("table");

  const sorted = useMemo(() => {
    return [...positions].sort((a, b) => {
      let av: number | string = a[sortKey];
      let bv: number | string = b[sortKey];

      // For date sort, convert to comparable value
      if (sortKey === "entryDate") {
        av = a.daysHeld; // more days held = earlier date
        bv = b.daysHeld;
        // invert because more daysHeld = earlier = should come first when asc
        const diff = (bv as number) - (av as number);
        return sortDir === "asc" ? diff : -diff;
      }

      if (typeof av === "number" && typeof bv === "number") {
        return sortDir === "asc" ? av - bv : bv - av;
      }
      const sa = String(av).toLowerCase();
      const sb = String(bv).toLowerCase();
      return sortDir === "asc"
        ? sa.localeCompare(sb)
        : sb.localeCompare(sa);
    });
  }, [positions, sortKey, sortDir]);

  function handleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  // For allocation chart: sort by weight descending
  const byWeight = useMemo(
    () => [...positions].sort((a, b) => b.weight - a.weight),
    [positions]
  );
  const maxWeight = byWeight[0]?.weight ?? 1;

  const tabBtn = (key: typeof tab, label: string) => (
    <button
      type="button"
      onClick={() => setTab(key)}
      className={[
        "rounded-full border px-3 py-1.5 text-sm transition",
        tab === key
          ? "bg-black text-white border-black"
          : "bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50",
      ].join(" ")}
    >
      {label}
    </button>
  );

  return (
    <div className="mx-auto max-w-6xl px-6 py-10 space-y-10">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl tracking-tight">Portfolio</h1>
        <p className="text-sm text-zinc-500">
          Live positions sourced from Google Sheets · {positions.length} holdings
        </p>
      </div>

      {/* Summary cards */}
      <section className="space-y-4">
        <h2 className="text-xl tracking-tight">Summary</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Invested"
            value={formatMoney(totalInvested)}
          />
          <MetricCard
            label="# of Holdings"
            value={String(positions.length)}
          />
          <MetricCard
            label="Avg Position Size"
            value={formatMoney(avgPositionSize)}
          />
          <MetricCard
            label="Largest Position"
            value={
              largestPosition
                ? `${largestPosition.ticker} (${formatMoney(largestPosition.costBasis)})`
                : "—"
            }
          />
        </div>
      </section>

      {/* Holdings + Allocation tabs */}
      <section className="space-y-4">
        <h2 className="text-xl tracking-tight">Holdings</h2>

        <div className="flex flex-wrap gap-2">
          {tabBtn("table", "Table")}
          {tabBtn("allocation", "Allocation")}
        </div>

        {tab === "table" && (
          <div className="rounded-2xl border border-zinc-200 bg-white overflow-hidden">
            {positions.length === 0 ? (
              <div className="px-6 py-10 text-zinc-500 text-sm">
                No position data available. The Google Sheet may be temporarily
                unreachable.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-zinc-50 text-zinc-600">
                    <tr className="text-left">
                      <SortButton col="ticker" label="Ticker" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                      <SortButton col="entryDate" label="Entry Date" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                      <SortButton col="daysHeld" label="Days Held" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                      <SortButton col="avgCost" label="Avg Cost" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                      <SortButton col="numShares" label="Shares" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                      <SortButton col="costBasis" label="Cost Basis" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                      <SortButton col="weight" label="Weight" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                    </tr>
                  </thead>
                  <tbody>
                    {sorted.map((p, idx) => (
                      <tr key={idx} className="border-t border-zinc-100">
                        <td className="px-4 py-3 font-semibold">{p.ticker}</td>
                        <td className="px-4 py-3 text-zinc-700 whitespace-nowrap">
                          {p.entryDate}
                        </td>
                        <td className="px-4 py-3 text-zinc-700">
                          {p.daysHeld > 0 ? `${p.daysHeld}d` : "—"}
                        </td>
                        <td className="px-4 py-3">{formatMoney(p.avgCost)}</td>
                        <td className="px-4 py-3">{formatNum(p.numShares)}</td>
                        <td className="px-4 py-3 font-semibold">
                          {formatMoney(p.costBasis)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 rounded-full bg-zinc-100 overflow-hidden">
                              <div
                                className="h-full rounded-full bg-zinc-900"
                                style={{
                                  width: `${Math.min(100, (p.weight / maxWeight) * 100)}%`,
                                }}
                              />
                            </div>
                            <span>{formatPct(p.weight)}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {tab === "allocation" && (
          <div className="rounded-2xl border border-zinc-200 bg-white p-5">
            {positions.length === 0 ? (
              <div className="text-zinc-500 text-sm">No data available.</div>
            ) : (
              <div className="space-y-0.5">
                <div className="flex items-center gap-3 pb-2 text-xs font-semibold text-zinc-500">
                  <div className="w-14 text-right">Ticker</div>
                  <div className="flex-1">Allocation</div>
                  <div className="w-16 text-right">Weight</div>
                  <div className="w-24 text-right">Cost Basis</div>
                </div>
                {byWeight.map((p) => (
                  <AllocationBar
                    key={p.ticker}
                    ticker={p.ticker}
                    weight={p.weight}
                    costBasis={p.costBasis}
                    maxWeight={maxWeight}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      {/* Data source note */}
      <p className="text-xs text-zinc-400 pb-4">
        Data sourced from Algory Capital Google Sheets. Prices reflect average
        cost basis at time of entry — not current market prices.
      </p>
    </div>
  );
}
