from polygon import RESTClient
from datetime import datetime, timedelta
import pandas as pd
from fastapi import FastAPI
from typing import List
import uvicorn


api_key = '2ZUdT7dCsR6Y630eg8D0AVqdhKo9U7Ci'
client = RESTClient(api_key)

class PairsTrading:
    def __init__(self, api_key):
        self.client = RESTClient(api_key)

    def get_daily_prices(self, ticker, days):

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        bars = self.client.get_aggs(ticker, 1, "day", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        data = [{'open': bar.open, 'high': bar.high, 'low': bar.low, 'close': bar.close, 'volume': bar.volume, 'timestamp': bar.timestamp} for bar in bars]
        return pd.DataFrame(data)

    def pairs_trading_strategy(self, tickers, days=30):

        # Fetch historical price data for each ticker
        price_data = {}
        for ticker in tickers:
            price_data[ticker] = self.get_daily_prices(ticker, days)
        
        # Standardize the closing prices for each ticker
        for ticker in tickers:
            price_data[ticker]['close'] = (price_data[ticker]['close'] - price_data[ticker]['close'].mean()) / price_data[ticker]['close'].std()
        
        # Merge dataframes on the timestamp
        merged_df = price_data[tickers[0]]
        for ticker in tickers[1:]:
            merged_df = pd.merge(merged_df, price_data[ticker], on='timestamp', suffixes=('', f'_{ticker}'))
        
        # Calculate the spread between the first two tickers' closing prices
        merged_df['spread'] = merged_df['close'] - merged_df[f'close_{tickers[1]}']
        
        # Calculate the mean and standard deviation of the spread
        spread_mean = merged_df['spread'].mean()
        spread_std = merged_df['spread'].std()
        
        # Define trading signals based on the spread
        merged_df['signal'] = 0
        merged_df.loc[merged_df['spread'] > spread_mean + spread_std, 'signal'] = -1  # Short first ticker, Long second ticker
        merged_df.loc[merged_df['spread'] < spread_mean - spread_std, 'signal'] = 1   # Long first ticker, Short second ticker
        
        return merged_df

    def auto_trading_decision(self, tickers, days=30):
        # Run the pairs trading strategy
        strategy_result = self.pairs_trading_strategy(tickers, days)
        
        # Get the latest signal
        latest_signal = strategy_result.iloc[-1]['signal']
        
        # Make a trading decision based on the signal
        if latest_signal == 1:
            decision = f"Buy {tickers[0]} and Sell {tickers[1]}"
        elif latest_signal == -1:
            decision = f"Sell {tickers[0]} and Buy {tickers[1]}"
        else:
            decision = "Hold positions"
        
        return decision

def get_current_trading_decision(tickers: List[str], days: int = 30):
    strategy = PairsTrading(api_key)
    return strategy.auto_trading_decision(tickers, days)