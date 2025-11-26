"""Real Market Data Adapters.

This module provides adapters to fetch real market data from various sources:
- yfinance: Stock and ETF data from Yahoo Finance
- ccxt: Cryptocurrency data from multiple exchanges

These adapters convert real market data into the format expected by
the backtesting engine and strategies.
"""

from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd


class YFinanceAdapter:
    """
    Adapter for Yahoo Finance data using yfinance library.
    
    Supports stocks, ETFs, indices, and forex.
    """
    
    def __init__(self):
        """Initialize yfinance adapter."""
        try:
            import yfinance as yf
            self.yf = yf
            self.available = True
        except ImportError:
            self.available = False
            print("⚠️  yfinance not installed. Run: pip install yfinance")
    
    def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1h'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data from Yahoo Finance.
        
        Args:
            symbol: Ticker symbol (e.g., 'AAPL', 'SPY', 'BTC-USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Data interval ('1m', '5m', '1h', '1d', etc.)
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        if not self.available:
            print("❌ yfinance not available")
            return None
        
        try:
            ticker = self.yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            if df.empty:
                print(f"⚠️  No data found for {symbol}")
                return None
            
            # Rename columns to match our format
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Ensure index is named 'timestamp'
            df.index.name = 'timestamp'
            
            # Keep only relevant columns
            df = df[['open', 'high', 'low', 'close', 'volume', 'symbol']]
            
            print(f"✅ Fetched {len(df)} bars for {symbol}")
            print(f"   Period: {df.index[0]} to {df.index[-1]}")
            print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return None
    
    def get_available_intervals(self) -> List[str]:
        """Get list of available data intervals."""
        return ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']


class CCXTAdapter:
    """
    Adapter for cryptocurrency data using ccxt library.
    
    Supports 100+ cryptocurrency exchanges.
    """
    
    def __init__(self, exchange_id: str = 'binance'):
        """
        Initialize CCXT adapter.
        
        Args:
            exchange_id: Exchange to use (e.g., 'binance', 'coinbase', 'kraken')
        """
        try:
            import ccxt
            self.ccxt = ccxt
            self.exchange = getattr(ccxt, exchange_id)()
            self.exchange_id = exchange_id
            self.available = True
            print(f"✅ Connected to {exchange_id}")
        except ImportError:
            self.available = False
            print("⚠️  ccxt not installed. Run: pip install ccxt")
        except Exception as e:
            self.available = False
            print(f"❌ Error initializing {exchange_id}: {e}")
    
    def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None,
        timeframe: str = '1h'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data from cryptocurrency exchange.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date (optional, defaults to now)
            timeframe: Candle timeframe ('1m', '5m', '1h', '1d', etc.)
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        if not self.available:
            print("❌ CCXT not available")
            return None
        
        try:
            # Convert dates to timestamps
            since = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            
            if end_date:
                until = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            else:
                until = int(datetime.now().timestamp() * 1000)
            
            # Fetch data in chunks (exchanges have limits)
            all_candles = []
            current_since = since
            
            while current_since < until:
                print(f"   Fetching from {datetime.fromtimestamp(current_since/1000)}")
                
                candles = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe=timeframe,
                    since=current_since,
                    limit=1000  # Max per request
                )
                
                if not candles:
                    break
                
                all_candles.extend(candles)
                
                # Move to next batch
                current_since = candles[-1][0] + 1
                
                # Stop if we've reached the end date
                if current_since >= until:
                    break
            
            if not all_candles:
                print(f"⚠️  No data found for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(
                all_candles,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Filter to requested date range
            df = df[(df.index >= start_date) & (df.index <= end_date if end_date else True)]
            
            print(f"✅ Fetched {len(df)} candles for {symbol}")
            print(f"   Period: {df.index[0]} to {df.index[-1]}")
            print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return None
    
    def get_available_timeframes(self) -> List[str]:
        """Get list of timeframes supported by the exchange."""
        if not self.available:
            return []
        
        return list(self.exchange.timeframes.keys()) if hasattr(self.exchange, 'timeframes') else []


def get_stock_data(symbol: str, days: int = 30, interval: str = '1h') -> Optional[pd.DataFrame]:
    """
    Quick helper to get stock data.
    
    Args:
        symbol: Stock ticker (e.g., 'AAPL', 'TSLA')
        days: Number of days of history
        interval: Data interval
        
    Returns:
        DataFrame with OHLCV data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    adapter = YFinanceAdapter()
    return adapter.fetch_ohlcv(
        symbol,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        interval=interval
    )


def get_crypto_data(symbol: str = 'BTC/USDT', days: int = 30, timeframe: str = '1h') -> Optional[pd.DataFrame]:
    """
    Quick helper to get cryptocurrency data.
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        days: Number of days of history
        timeframe: Candle timeframe
        
    Returns:
        DataFrame with OHLCV data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    adapter = CCXTAdapter('binance')
    return adapter.fetch_ohlcv(
        symbol,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        timeframe=timeframe
    )


if __name__ == "__main__":
    print("=" * 70)
    print("📊 Real Data Adapters Demo")
    print("=" * 70)
    print()
    
    # Test yfinance
    print("1️⃣  Testing Yahoo Finance (Stock Data)")
    print("-" * 70)
    stock_data = get_stock_data('AAPL', days=7, interval='1h')
    if stock_data is not None:
        print(f"\nSample data (first 3 rows):")
        print(stock_data.head(3))
    print()
    
    # Test ccxt
    print("2️⃣  Testing CCXT (Crypto Data)")
    print("-" * 70)
    crypto_data = get_crypto_data('BTC/USDT', days=7, timeframe='1h')
    if crypto_data is not None:
        print(f"\nSample data (first 3 rows):")
        print(crypto_data.head(3))
    print()
