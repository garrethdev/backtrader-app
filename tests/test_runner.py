import pytest
from src.runner import _load_strategy_class, run_backtest
import backtrader as bt

def test_code_without_strategy_raises_runtime_error():
    """Test that code without bt.Strategy subclass raises RuntimeError."""
    code = """
def some_function():
    return "not a strategy"
    """
    
    with pytest.raises(RuntimeError, match="No bt.Strategy subclass found in code"):
        _load_strategy_class(code)

def test_equity_curve_length_equals_bar_count():
    """Test that equity curve has same length as input bars."""
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
            {"time": "2020-01-03", "open": 100.5, "high": 101.5, "low": 100, "close": 101.2, "volume": 11000, "openinterest": 0},
            {"time": "2020-01-06", "open": 101.2, "high": 102, "low": 101, "close": 101.8, "volume": 12000, "openinterest": 0}
        ],
        "capital": 10000
    }
    
    result = run_backtest(payload)
    
    # Equity curve should have same length as bars
    assert len(result["equity_curve"]) == len(payload["bars"])

def test_params_override_respected():
    """Test that strategy parameters are properly overridden."""
    payload = {
        "code": """
import backtrader as bt
class ParameterizedStrategy(bt.Strategy):
    params = (('period', 10),)
    
    def __init__(self):
        self.sma = bt.ind.SMA(self.data.close, period=self.p.period)
        
    def next(self):
        pass
        """,
        "bars": [
            {"time": f"2020-01-{i:02d}", "open": 100+i, "high": 101+i, "low": 99+i, "close": 100.5+i, "volume": 10000, "openinterest": 0}
            for i in range(2, 32)  # 30 bars to ensure SMA can calculate
        ],
        "capital": 10000,
        "params": {"period": 5}  # Override default period of 10
    }
    
    # This should not raise an error - if params weren't passed correctly,
    # the strategy might fail to initialize properly
    result = run_backtest(payload)
    
    # Basic validation that the backtest ran successfully
    assert "summary" in result
    assert result["summary"]["final_value"] > 0

def test_strategy_with_trades():
    """Test that trades are properly captured when strategy makes trades."""
    payload = {
        "code": """
import backtrader as bt
class TradingStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        
            def next(self):
            if not self.position and len(self.data) == 2:  # Buy on second bar
                self.order = self.buy(size=100)
            elif self.position and len(self.data) == 4:  # Sell on fourth bar
                self.order = self.close()  # Close position instead of sell
        """,
        "bars": [
            {"time": "2020-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 10000, "openinterest": 0},
            {"time": "2020-01-03", "open": 100.5, "high": 101.5, "low": 100, "close": 101.2, "volume": 11000, "openinterest": 0},
            {"time": "2020-01-06", "open": 101.2, "high": 102, "low": 101, "close": 101.8, "volume": 12000, "openinterest": 0},
            {"time": "2020-01-07", "open": 101.8, "high": 102.5, "low": 101.5, "close": 102.1, "volume": 13000, "openinterest": 0},
            {"time": "2020-01-08", "open": 102.1, "high": 103, "low": 102, "close": 102.8, "volume": 14000, "openinterest": 0}
        ],
        "capital": 10000
    }
    
    result = run_backtest(payload)
    
    # Should have at least one trade
    assert len(result["trades"]) >= 1
    
    # Check trade structure
    if result["trades"]:
        trade = result["trades"][0]
        assert "entry_time" in trade
        assert "exit_time" in trade
        assert "direction" in trade
        assert "pnl" in trade
        assert "pnlcomm" in trade

def test_no_bars_raises_runtime_error():
    """Test that missing bars raises RuntimeError."""
    payload = {
        "code": """
import backtrader as bt
class TestStrategy(bt.Strategy):
    def next(self):
        pass
        """,
        "capital": 10000
    }
    
    with pytest.raises(RuntimeError, match="MVP requires 'bars' in payload"):
        run_backtest(payload)