import { Card } from "./ui/card";
import { TrendingUp, TrendingDown, Activity, DollarSign, Percent, Calendar } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  icon: React.ReactNode;
}

function MetricCard({ title, value, change, isPositive, icon }: MetricCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-muted-foreground mb-1">{title}</p>
          <h3>{value}</h3>
          {change && (
            <div className={`flex items-center gap-1 mt-2 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              <span>{change}</span>
            </div>
          )}
        </div>
        <div className="text-muted-foreground">
          {icon}
        </div>
      </div>
    </Card>
  );
}

interface PerformanceMetricsProps {
  metrics: {
    totalReturn: number;
    annualizedReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    totalTrades: number;
  };
}

export function PerformanceMetrics({ metrics }: PerformanceMetricsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <MetricCard
        title="Total Return"
        value={`${metrics.totalReturn > 0 ? '+' : ''}${metrics.totalReturn.toFixed(2)}%`}
        change={`${metrics.annualizedReturn.toFixed(2)}% annualized`}
        isPositive={metrics.totalReturn > 0}
        icon={<DollarSign className="h-6 w-6" />}
      />
      <MetricCard
        title="Sharpe Ratio"
        value={metrics.sharpeRatio.toFixed(2)}
        isPositive={metrics.sharpeRatio > 1}
        icon={<Activity className="h-6 w-6" />}
      />
      <MetricCard
        title="Max Drawdown"
        value={`${metrics.maxDrawdown.toFixed(2)}%`}
        isPositive={false}
        icon={<TrendingDown className="h-6 w-6" />}
      />
      <MetricCard
        title="Win Rate"
        value={`${metrics.winRate.toFixed(1)}%`}
        isPositive={metrics.winRate > 50}
        icon={<Percent className="h-6 w-6" />}
      />
      <MetricCard
        title="Total Trades"
        value={metrics.totalTrades}
        icon={<Calendar className="h-6 w-6" />}
      />
      <MetricCard
        title="Profit Factor"
        value={(1 + metrics.totalReturn / 100).toFixed(2)}
        isPositive={metrics.totalReturn > 0}
        icon={<TrendingUp className="h-6 w-6" />}
      />
    </div>
  );
}
