import { Card } from "./ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface EquityChartProps {
  data: Array<{
    date: string;
    equity: number;
    benchmark: number;
  }>;
}

export function EquityChart({ data }: EquityChartProps) {
  return (
    <Card className="p-6">
      <h3 className="mb-4">Equity Curve</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="date" 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px'
            }}
            formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="equity" 
            stroke="hsl(var(--chart-1))" 
            strokeWidth={2}
            name="Strategy"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="benchmark" 
            stroke="hsl(var(--chart-2))" 
            strokeWidth={2}
            name="Benchmark"
            dot={false}
            strokeDasharray="5 5"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
