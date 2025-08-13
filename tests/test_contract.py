import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_valid_bars_payload_returns_200():
    """Test that a valid bars payload returns 200 with expected response structure."""
    payload = {
        "code": """
import backtrader as bt
class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.ind.SMA(self.data.close, period=5)
    def next(self):
        if not self.position:
            self.buy()
        """,
        "bars": [
            {"time": "2020-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 10000, "openinterest": 0},
            {"time": "2020-01-03", "open": 100.5, "high": 101.5, "low": 100, "close": 101.2, "volume": 11000, "openinterest": 0},
            {"time": "2020-01-06", "open": 101.2, "high": 102, "low": 101, "close": 101.8, "volume": 12000, "openinterest": 0}
        ],
        "capital": 10000
    }
    
    response = client.post("/run", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that all required keys are present
    assert "ohlcv" in data
    assert "trades" in data
    assert "equity_curve" in data
    assert "summary" in data
    
    # Check summary structure
    summary = data["summary"]
    assert "final_value" in summary
    assert "return_pct" in summary
    assert "total_trades" in summary
    assert "win_rate" in summary
    assert "max_drawdown_pct" in summary
    assert "sharpe" in summary

def test_missing_code_returns_400():
    """Test that missing code parameter returns 400 error."""
    payload = {
        "bars": [
            {"time": "2020-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 10000, "openinterest": 0}
        ]
    }
    
    response = client.post("/run", json=payload)
    assert response.status_code == 422  # FastAPI validation error
    assert "Field required" in str(response.json())

def test_symbol_dates_only_returns_501():
    """Test that providing only symbol and dates (without bars) returns 501."""
    payload = {
        "code": """
import backtrader as bt
class TestStrategy(bt.Strategy):
    def next(self):
        pass
        """,
        "symbol": "AAPL",
        "start_date": "2020-01-01",
        "end_date": "2020-01-31"
    }
    
    response = client.post("/run", json=payload)
    assert response.status_code == 501
    assert "symbol-based data loading not implemented" in response.json()["detail"]

def test_empty_payload_returns_422():
    """Test that completely empty payload returns 422 (validation error)."""
    response = client.post("/run", json={})
    assert response.status_code == 422  # FastAPI validation error