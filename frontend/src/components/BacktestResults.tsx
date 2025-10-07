import { PerformanceMetrics } from "./PerformanceMetrics";
import { EquityChart } from "./EquityChart";
import { DrawdownChart } from "./DrawdownChart";
import { ReturnsDistribution } from "./ReturnsDistribution";
import { TradeHistory } from "./TradeHistory";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

interface BacktestResultsProps {
  results: {
    metrics: {
      totalReturn: number;
      annualizedReturn: number;
      sharpeRatio: number;
      maxDrawdown: number;
      winRate: number;
      totalTrades: number;
    };
    equityData: Array<{
      date: string;
      equity: number;
      benchmark: number;
    }>;
    drawdownData: Array<{
      date: string;
      drawdown: number;
    }>;
    returnsDistribution: Array<{
      range: string;
      count: number;
    }>;
    trades: Array<{
      id: number;
      date: string;
      type: 'BUY' | 'SELL';
      symbol: string;
      quantity: number;
      price: number;
      pnl?: number;
    }>;
  };
}

export function BacktestResults({ results }: BacktestResultsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="mb-2">Backtest Results</h2>
        <p className="text-muted-foreground">
          Analysis of your trading strategy performance
        </p>
      </div>

      <PerformanceMetrics metrics={results.metrics} />

      <Tabs defaultValue="equity" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="equity">Equity Curve</TabsTrigger>
          <TabsTrigger value="drawdown">Drawdown</TabsTrigger>
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
          <TabsTrigger value="trades">Trades</TabsTrigger>
        </TabsList>
        <TabsContent value="equity" className="mt-6">
          <EquityChart data={results.equityData} />
        </TabsContent>
        <TabsContent value="drawdown" className="mt-6">
          <DrawdownChart data={results.drawdownData} />
        </TabsContent>
        <TabsContent value="distribution" className="mt-6">
          <ReturnsDistribution data={results.returnsDistribution} />
        </TabsContent>
        <TabsContent value="trades" className="mt-6">
          <TradeHistory trades={results.trades} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
