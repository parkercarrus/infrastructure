import { Card } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";

interface Trade {
  id: number;
  date: string;
  type: 'BUY' | 'SELL';
  symbol: string;
  quantity: number;
  price: number;
  pnl?: number;
}

interface TradeHistoryProps {
  trades: Trade[];
}

export function TradeHistory({ trades }: TradeHistoryProps) {
  return (
    <Card className="p-6">
      <h3 className="mb-4">Trade History</h3>
      <div className="rounded-lg border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Symbol</TableHead>
              <TableHead>Quantity</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>P&L</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trades.map((trade) => (
              <TableRow key={trade.id}>
                <TableCell>{trade.date}</TableCell>
                <TableCell>
                  <Badge 
                    variant={trade.type === 'BUY' ? 'default' : 'secondary'}
                  >
                    {trade.type}
                  </Badge>
                </TableCell>
                <TableCell>{trade.symbol}</TableCell>
                <TableCell>{trade.quantity}</TableCell>
                <TableCell>${trade.price.toFixed(2)}</TableCell>
                <TableCell>
                  {trade.pnl !== undefined ? (
                    <span className={trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                    </span>
                  ) : (
                    <span className="text-muted-foreground">-</span>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}
