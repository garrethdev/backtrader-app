#!/usr/bin/env python3
"""
Debug the failing test to see the actual error
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def debug_failing_test():
    """Run the exact same test that's failing to see the error"""
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
    
    print("🔍 Testing the exact failing payload...")
    response = client.post("/run", json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("❌ This is the error we need to fix!")
    else:
        print("✅ Actually works fine")

if __name__ == "__main__":
    debug_failing_test()