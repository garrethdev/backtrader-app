#!/usr/bin/env python3
"""
Simple validation script to test basic functionality without running the full test suite.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.schemas import RunRequest, RunResponse, Bar
        from src.runner import run_backtest, _load_strategy_class
        from src.utils.datafeed import bars_to_temp_csv
        from src.main import app
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_strategy_loading():
    """Test that strategy code can be loaded."""
    try:
        from src.runner import _load_strategy_class
        code = """
import backtrader as bt
class TestStrategy(bt.Strategy):
    def __init__(self):
        pass
    def next(self):
        pass
        """
        strategy_class = _load_strategy_class(code)
        print(f"✓ Strategy loading successful: {strategy_class.__name__}")
        return True
    except Exception as e:
        print(f"✗ Strategy loading failed: {e}")
        return False

def test_basic_backtest():
    """Test basic backtest functionality."""
    try:
        from src.runner import run_backtest
        payload = {
            "code": """
import backtrader as bt
class SimpleStrategy(bt.Strategy):
    def __init__(self):
        pass
    def next(self):
        pass
            """,
            "bars": [
                {"time": "2020-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 10000, "openinterest": 0},
                {"time": "2020-01-03", "open": 100.5, "high": 101.5, "low": 100, "close": 101.2, "volume": 11000, "openinterest": 0}
            ],
            "capital": 10000
        }
        
        result = run_backtest(payload)
        
        # Check result structure
        required_keys = ["ohlcv", "trades", "equity_curve", "summary"]
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing key: {key}")
        
        print("✓ Basic backtest successful")
        print(f"  - Final value: {result['summary']['final_value']}")
        print(f"  - Equity curve points: {len(result['equity_curve'])}")
        return True
    except Exception as e:
        print(f"✗ Basic backtest failed: {e}")
        return False

def main():
    print("Validating Backtrader Service...")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_strategy_loading, 
        test_basic_backtest
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validations passed! Service is ready.")
        return 0
    else:
        print("❌ Some validations failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())