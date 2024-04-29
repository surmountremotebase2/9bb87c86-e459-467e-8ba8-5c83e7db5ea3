from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV
import pandas as pd
import numpy as np

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the S&P 500 stock universe; in practice, this list should be dynamic.
        self.sp500_tickers = ["AAPL", "MSFT", "AMZN", "FB", "GOOGL", "..."]  # Example tickers
        self.lookback_period = 20  # Lookback period in days to calculate volatility
        self.top_n = 10  # Number of top volatile stocks to go long

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.sp500_tickers

    @property
    def data(self):
        # Add OHLCV data requirement for each ticker
        return [OHLCV(ticker) for ticker in self.sp500_tickers]

    def run(self, data):
        volatilities = {}
        for ticker in self.sp500_tickers:
            if ticker in data:
                prices = pd.Series([x['close'] for x in data[ticker]])
                returns = prices.pct_change().dropna()
                volatilities[ticker] = returns.std()  # Standard deviation as volatility measure

        # Rank stocks by volatility
        ranked_by_volatility = sorted(volatilities.items(), key=lambda x: x[1], reverse=True)

        # Select top N volatile stocks
        top_volatile_stocks = ranked_by_volatility[:self.top_n]

        # Calculate equal allocation for each selected stock
        allocation = {ticker: 1 / self.top_n for ticker, _ in top_volatile_stocks}

        # Construct and return the target allocation
        return TargetAllocation(allocation)

    def should_rebalance(self, data):
        """Determine if the portfolio should be rebalanced.
        
        This method checks if it's the first trading day of the month.
        """
        current_date = pd.to_datetime(data["timestamp"])
        first_day_of_month = current_date.replace(day=1)
        return current_date == first_day_of_month