import { useState } from "react";
import { FileUpload } from "./components/FileUpload";
import { BacktestResults } from "./components/BacktestResults";
import { GalaxyBackground } from "./components/GalaxyBackground";
import { Button } from "./components/ui/button";
import { BarChart3, ArrowLeft } from "lucide-react";

// Mock data generator for demonstration
function generateMockResults() {
  const equityData = [];
  const drawdownData = [];
  let equity = 100000;
  let peak = equity;
  
  for (let i = 0; i < 252; i++) {
    const date = new Date(2024, 0, 1 + i).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const change = (Math.random() - 0.45) * 1000;
    equity += change;
    peak = Math.max(peak, equity);
    const drawdown = ((equity - peak) / peak) * 100;
    
    equityData.push({
      date,
      equity: Math.round(equity),
      benchmark: Math.round(100000 + i * 150 + Math.random() * 500)
    });
    
    drawdownData.push({
      date,
      drawdown: Math.round(drawdown * 100) / 100
    });
  }

  const returnsDistribution = [
    { range: '-5% to -3%', count: 8 },
    { range: '-3% to -1%', count: 15 },
    { range: '-1% to 0%', count: 22 },
    { range: '0% to 1%', count: 28 },
    { range: '1% to 3%', count: 18 },
    { range: '3% to 5%', count: 11 }
  ];

  const trades = [];
  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];
  
  for (let i = 0; i < 50; i++) {
    const isSell = i % 2 === 1;
    trades.push({
      id: i + 1,
      date: new Date(2024, 0, 1 + i * 5).toLocaleDateString('en-US'),
      type: isSell ? 'SELL' : 'BUY' as 'BUY' | 'SELL',
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      quantity: Math.floor(Math.random() * 100) + 10,
      price: Math.random() * 500 + 100,
      pnl: isSell ? (Math.random() - 0.4) * 2000 : undefined
    });
  }

  const totalReturn = ((equity - 100000) / 100000) * 100;
  
  return {
    metrics: {
      totalReturn,
      annualizedReturn: totalReturn,
      sharpeRatio: 1.2 + Math.random() * 0.8,
      maxDrawdown: -12.5,
      winRate: 58.3,
      totalTrades: 50
    },
    equityData,
    drawdownData,
    returnsDistribution,
    trades
  };
}

export default function App() {
  const [results, setResults] = useState<ReturnType<typeof generateMockResults> | null>(null);

  const handleFileUpload = (file: File) => {
    // Simulate processing the file
    setTimeout(() => {
      setResults(generateMockResults());
    }, 1000);
  };

  const handleCodePaste = (code: string) => {
    // Simulate processing the code
    setTimeout(() => {
      setResults(generateMockResults());
    }, 1000);
  };

  const handleReset = () => {
    setResults(null);
  };

  return (
    <div className="min-h-screen bg-transparent relative">
      <GalaxyBackground />
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm relative z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-8 w-8 text-primary" />
              <div>
                <h1>AlgoBacktest</h1>
                <p className="text-muted-foreground">
                  Algorithmic Trading Model Backtesting Platform
                </p>
              </div>
            </div>
            {results && (
              <Button onClick={handleReset} variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                New Backtest
              </Button>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {!results ? (
          <div className="max-w-3xl mx-auto">
            <div className="mb-8">
              <h2 className="mb-2">Upload Your Trading Model</h2>
              <p className="text-muted-foreground">
                Upload your algorithmic trading model to analyze its performance with comprehensive backtesting metrics and visualizations.
              </p>
            </div>
            <FileUpload 
              onFileUpload={handleFileUpload}
              onCodePaste={handleCodePaste}
            />
          </div>
        ) : (
          <BacktestResults results={results} />
        )}
      </main>
    </div>
  );
}
