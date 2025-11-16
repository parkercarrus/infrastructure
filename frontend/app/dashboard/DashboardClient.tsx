"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";


type PortfolioEntry = {
  timestamp: string;        // Original ISO timestamp from API
  total_value: number;
  total_cash: number;
  total_positions: number;
  ts: number;               // Converted numeric timestamp (ms)
};
type TradeEntry = {
  trade_id: number;
  timestamp: string;
  strategy: string;
  symbol: string;
  side: string;
  quantity: number;
  price: number;
  ts: number;       // numeric timestamp for sorting/display
};

export default function DashboardClient() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && window.matchMedia) {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      setDarkMode(mq.matches);
      const listener = (e: MediaQueryListEvent) => setDarkMode(e.matches);
      mq.addEventListener("change", listener);
      return () => mq.removeEventListener("change", listener);
    }
  }, []);


  const [portfolioHistory, setPortfolioHistory] = useState<PortfolioEntry[]>([]);
  const [trades, setTrades] = useState<TradeEntry[]>([]);

  useEffect(() => {
    async function loadPortfolio() {
      try {
        const res = await fetch(`${API_URL}/portfolio`);
        const json: Omit<PortfolioEntry, "ts">[] = await res.json();

        const processed: PortfolioEntry[] = json.map((d) => ({
          ...d,
          ts: new Date(d.timestamp.replace(/\.\d+$/, "")).getTime()
        }));

        setPortfolioHistory(processed);
      } catch (err) {
        console.error("Portfolio fetch error:", err);
      }
    }

    loadPortfolio();
    const id = setInterval(loadPortfolio, 10000);
    return () => clearInterval(id);
  }, []);

useEffect(() => {
  async function loadTrades() {
    try {
      const res = await fetch(`${API_URL}/trades`);
      const json: Omit<TradeEntry, "ts">[] = await res.json();

      const processed: TradeEntry[] = json.map((t) => ({
        ...t,
        ts: new Date(t.timestamp.replace(/\.\d+$/, "")).getTime(),
      }));

      // Sort newest → oldest
      processed.sort((a, b) => b.ts - a.ts);

      setTrades(processed);
    } catch (err) {
      console.error("Trades fetch error:", err);
    }
  }

  loadTrades();
  const id = setInterval(loadTrades, 2000); // update every 2s
  return () => clearInterval(id);
}, []);

  const latest: PortfolioEntry | null =
    portfolioHistory.length > 0
      ? portfolioHistory[portfolioHistory.length - 1]
      : null;

  /* ---------------------------------------------
     MAIN RENDER
  --------------------------------------------- */
  return (
    <main className="min-h-screen bg-white text-black dark:bg-zinc-900 dark:text-white px-6 py-8 font-mono">

      {/* Header */}
      <div
        className="border border-black rounded-lg p-4 flex justify-between items-end mb-12 bg-background"
      >
        <h1 className="text-3xl font-bold tracking-tight">Algory Capital Algorithmic Portfolio</h1>
        <div>
          <Link href="/" className="hover:underline dark:text-white mr-4">
            Home
          </Link>
          <Link href="/about" className="hover:underline dark:text-white mr-4">
            About
          </Link>
        </div>
      </div>

      {/* Portfolio Chart */}
      <Card className="border border-black dark:border-white mb-6 bg-white dark:bg-zinc-800">
        <CardContent className="pt-4">
          <h2 className="text-xl font-semibold mb-2">Portfolio Performance Over Time</h2>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={portfolioHistory}>
              <XAxis
                dataKey="ts"
                type="number"
                domain={["auto", "auto"]}
                tickFormatter={(t) => new Date(t).toLocaleTimeString()}
                axisLine={false}
                tickLine={false}
              />
              <YAxis domain={["auto", "auto"]} tickCount={8} />
              <Tooltip labelFormatter={(t) => new Date(t).toLocaleTimeString()} />
              <Legend />

              <Line
                type="monotone"
                dataKey="total_value"
                name="Total Value"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="total_cash"
                name="Cash"
                stroke="#16a34a"
                strokeWidth={2}
                dot={false}
              />

              <Line
                type="monotone"
                dataKey="total_positions"
                name="Positions"
                stroke="#dc2626"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Positions + Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Current Positions */}
    <Card className="border border-black dark:border-white bg-white dark:bg-zinc-800 mt-6">
      <CardContent className="pt-4">
        <h2 className="text-xl font-semibold mb-4">Trade History</h2>

        <div className="grid grid-cols-5 font-bold border-b border-black dark:border-white pb-1 mb-2 text-sm">
          <div>Symbol</div>
          <div>Side</div>
          <div>Qty @ Price</div>
          <div>Time</div>
          <div>Strategy</div>
        </div>

        <div className="flex flex-col gap-2 text-sm max-h-[260px] overflow-y-auto pr-2">

          {trades.length > 0 ? (
            trades.map((t) => (
              <div
                key={t.trade_id}
                className="grid grid-cols-5 border-b border-gray-300 dark:border-zinc-700 py-1"
              >
                <div>{t.symbol}</div>
                <div className={t.side === "BUY" ? "text-green-600" : "text-red-600"}>
                  {t.side}
                </div>
                <div>
                  {t.quantity.toFixed(3)} @ ${t.price.toFixed(2)}
                </div>
                <div className="truncate">{new Date(t.ts).toLocaleTimeString()}</div>
                <div>{t.strategy}</div>

              </div>
            ))
          ) : (
            <div className="text-gray-500 italic dark:text-zinc-400">
              No trades yet
            </div>
          )}

        </div>
      </CardContent>
    </Card>

        {/* Current Statistics */}
        <Card className="border border-black dark:border-white bg-white dark:bg-zinc-800">
          <CardContent className="pt-4">
            <h2 className="text-xl font-semibold mb-4">Current Statistics</h2>

            {latest ? (
              <div className="grid grid-cols-2 gap-x-10 gap-y-3 text-sm">

                <div className="flex justify-between">
                  <span className="text-zinc-500">Total Value</span>
                  <span className="font-semibold tabular-nums">
                    {latest.total_value.toFixed(3)}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-zinc-500">Cash</span>
                  <span className="font-semibold tabular-nums">
                    {latest.total_cash.toFixed(3)}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-zinc-500">Positions</span>
                  <span className="font-semibold tabular-nums">
                    {latest.total_positions}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-zinc-500">Timestamp</span>
                  <span className="font-semibold tabular-nums">
                    {new Date(latest.timestamp).toLocaleTimeString()}
                  </span>
                </div>

              </div>
            ) : (
              <div className="text-gray-500 italic">No statistics available</div>
            )}
          </CardContent>
        </Card>

      </div>
    </main>
  );
}
