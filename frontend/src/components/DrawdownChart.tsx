import { Card } from "./ui/card";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface DrawdownChartProps {
  data: Array<{
    date: string;
    drawdown: number;
  }>;
}

export function DrawdownChart({ data }: DrawdownChartProps) {
  return (
    <Card className="p-6">
      <h3 className="mb-4">Drawdown Analysis</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="date" 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px'
            }}
            formatter={(value: number) => [`${value.toFixed(2)}%`, 'Drawdown']}
          />
          <Area 
            type="monotone" 
            dataKey="drawdown" 
            stroke="hsl(var(--destructive))" 
            fillOpacity={1} 
            fill="url(#colorDrawdown)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}
