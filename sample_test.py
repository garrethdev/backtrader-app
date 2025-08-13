#!/usr/bin/env python3
"""
Sample usage demonstration for the Backtrader Service.
This script shows how to use the service programmatically.
"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.runner import run_backtest

def create_sample_bars():
    """Create sample OHLCV data for testing."""
    return [
        {"time": "2020-01-02", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 10000, "openinterest": 0},
        {"time": "2020-01-03", "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0, "volume": 11000, "openinterest": 0},
        {"time": "2020-01-06", "open": 102.0, "high": 104.0, "low": 101.0, "close": 103.0, "volume": 12000, "openinterest": 0},
        {"time": "2020-01-07", "open": 103.0, "high": 105.0, "low": 102.0, "close": 104.0, "volume": 13000, "openinterest": 0},
        {"time": "2020-01-08", "open": 104.0, "high": 106.0, "low": 103.0, "close": 105.0, "volume": 14000, "openinterest": 0},
        {"time": "2020-01-09", "open": 105.0, "high": 107.0, "low": 104.0, "close": 106.0, "volume": 15000, "openinterest": 0},
        {"time": "2020-01-10", "open": 106.0, "high": 108.0, "low": 105.0, "close": 107.0, "volume": 16000, "openinterest": 0},
        {"time": "2020-01-13", "open": 107.0, "high": 109.0, "low": 106.0, "close": 108.0, "volume": 17000, "openinterest": 0},
        {"time": "2020-01-14", "open": 108.0, "high": 110.0, "low": 107.0, "close": 109.0, "volume": 18000, "openinterest": 0},
        {"time": "2020-01-15", "open": 109.0, "high": 111.0, "low": 108.0, "close": 110.0, "volume": 19000, "openinterest": 0},
    ]

def sample_sma_crossover_strategy():
    """Simple Moving Average crossover strategy."""
    return """
import backtrader as bt

class SMACrossStrategy(bt.Strategy):
    params = (
        ('fast_period', 3),
        ('slow_period', 5),
        ('stake', 100),
    )
    
    def __init__(self):
        self.fast_sma = bt.ind.SMA(self.data.close, period=self.p.fast_period)
        self.slow_sma = bt.ind.SMA(self.data.close, period=self.p.slow_period)
        self.crossover = bt.ind.CrossOver(self.fast_sma, self.slow_sma)
        
    def next(self):
        if not self.position:
            if self.crossover > 0:  # Fast SMA crosses above slow SMA
                self.buy(size=self.p.stake)
        else:
            if self.crossover < 0:  # Fast SMA crosses below slow SMA
                self.sell(size=self.p.stake)
    """

def sample_buy_and_hold_strategy():
    """Simple buy and hold strategy."""
    return """
import backtrader as bt

class BuyAndHoldStrategy(bt.Strategy):
    params = (('stake', 1000),)
    
    def __init__(self):
        self.order = None
        
    def next(self):
        if not self.position and self.order is None:
            # Buy on the first opportunity
            self.order = self.buy(size=self.p.stake)
    """

def run_sample_test(strategy_name, strategy_code, params=None):
    """Run a sample backtest and display results."""
    print(f"\n{'='*60}")
    print(f"Testing: {strategy_name}")
    print('='*60)
    
    payload = {
        "code": strategy_code,
        "bars": create_sample_bars(),
        "symbol": "SAMPLE",
        "capital": 100000,
        "params": params or {}
    }
    
    try:
        result = run_backtest(payload)
        
        print(f"📊 Backtest Results:")
        print(f"   Initial Capital: ${payload['capital']:,.2f}")
        print(f"   Final Value: ${result['summary']['final_value']:,.2f}")
        print(f"   Return: {result['summary']['return_pct']:.2f}%")
        print(f"   Total Trades: {result['summary']['total_trades']}")
        print(f"   Win Rate: {result['summary']['win_rate']:.2f}")
        print(f"   Max Drawdown: {result['summary']['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe Ratio: {result['summary']['sharpe']:.4f}")
        
        if result['trades']:
            print(f"\n📈 Sample Trades:")
            for i, trade in enumerate(result['trades'][:3]):  # Show first 3 trades
                print(f"   Trade {i+1}: {trade['direction']} | "
                      f"Entry: {trade['entry_time']} | Exit: {trade['exit_time']} | "
                      f"PnL: ${trade['pnl']:.2f}")
        
        print(f"\n📉 Equity Curve Points: {len(result['equity_curve'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("Backtrader Service - Sample Usage Demonstration")
    print("This demonstrates the core functionality of the service.")
    
    # Test 1: SMA Crossover Strategy
    success1 = run_sample_test(
        "SMA Crossover Strategy",
        sample_sma_crossover_strategy(),
        {"fast_period": 3, "slow_period": 5, "stake": 100}
    )
    
    # Test 2: Buy and Hold Strategy
    success2 = run_sample_test(
        "Buy and Hold Strategy", 
        sample_buy_and_hold_strategy(),
        {"stake": 1000}
    )
    
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"SMA Crossover Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Buy & Hold Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All sample tests completed successfully!")
        print("The Backtrader Service is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())