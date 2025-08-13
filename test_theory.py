#!/usr/bin/env python3
"""
Test the theory about the SMA period vs bars count
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_with_enough_bars():
    """Test with enough bars for SMA(5)"""
    payload = {
        "code": """
import backtrader as bt
class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.ind.SMA(self.data.close, period=5)
    def next(self):
        if len(self.data) > 5 and not self.position:  # Wait for SMA to be ready
            self.buy()
        """,
        "bars": [
            {"time": f"2020-01-{i:02d}", "open": 100+i*0.1, "high": 101+i*0.1, "low": 99+i*0.1, "close": 100.5+i*0.1, "volume": 10000, "openinterest": 0}
            for i in range(2, 8)  # 6 bars (enough for SMA period=5)
        ],
        "capital": 10000
    }
    
    print("🧪 Test 1: Enough bars + wait for SMA")
    response = client.post("/run", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("✅ Success with enough bars")

def test_with_shorter_sma():
    """Test with shorter SMA period"""
    payload = {
        "code": """
import backtrader as bt
class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.ind.SMA(self.data.close, period=2)  # Shorter period
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
    
    print("\n🧪 Test 2: Shorter SMA period")
    response = client.post("/run", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("✅ Success with shorter SMA")

if __name__ == "__main__":
    test_with_enough_bars()
    test_with_shorter_sma()