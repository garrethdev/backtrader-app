#!/usr/bin/env python3
"""
Debug test to isolate the issue
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.runner import run_backtest

def debug_test():
    """Simple debug test with minimal data"""
    print("🔍 Debug Test - Minimal Example")
    
    # Very simple strategy
    code = """
import backtrader as bt
class DebugStrategy(bt.Strategy):
    def __init__(self):
        pass
    def next(self):
        pass
    """
    
    # Minimal bars data
    bars = [
        {"time": "2020-01-02", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000, "openinterest": 0},
        {"time": "2020-01-03", "open": 100.5, "high": 101.5, "low": 100.0, "close": 101.0, "volume": 1100, "openinterest": 0}
    ]
    
    payload = {
        "code": code,
        "bars": bars,
        "capital": 10000
    }
    
    print(f"Testing with {len(bars)} bars...")
    
    try:
        result = run_backtest(payload)
        print("✅ Debug test successful!")
        print(f"   Final value: {result['summary']['final_value']}")
        return True
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_test()