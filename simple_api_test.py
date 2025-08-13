#!/usr/bin/env python3
"""
Simple API test to isolate the issue
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_simple_api():
    """Test with the exact same data that works in debug_test.py"""
    print("🧪 Simple API Test")
    
    payload = {
        "code": """
import backtrader as bt
class DebugStrategy(bt.Strategy):
    def __init__(self):
        pass
    def next(self):
        pass
        """,
        "capital": 10000,
        "bars": [
            {"time": "2020-01-02", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000, "openinterest": 0},
            {"time": "2020-01-03", "open": 100.5, "high": 101.5, "low": 100.0, "close": 101.0, "volume": 1100, "openinterest": 0}
        ]
    }
    
    print("📤 Testing simple payload via FastAPI...")
    response = client.post("/run", json=payload)
    
    print(f"📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Simple API test successful!")
        print(f"   Final Value: {data['summary']['final_value']}")
        return True
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"   Details: {response.text}")
        return False

def test_with_sma_strategy():
    """Test with SMA strategy"""
    print("\n🧪 SMA Strategy API Test")
    
    payload = {
        "code": """
import backtrader as bt
class SMAStrategy(bt.Strategy):
    params = (('period', 3),)
    
    def __init__(self):
        self.sma = bt.ind.SMA(self.data.close, period=self.p.period)
        
    def next(self):
        pass  # Just calculate SMA, no trades
        """,
        "capital": 10000,
        "params": {"period": 2},
        "bars": [
            {"time": "2020-01-02", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000, "openinterest": 0},
            {"time": "2020-01-03", "open": 100.5, "high": 101.5, "low": 100.0, "close": 101.0, "volume": 1100, "openinterest": 0},
            {"time": "2020-01-06", "open": 101.0, "high": 102.0, "low": 100.5, "close": 101.5, "volume": 1200, "openinterest": 0}
        ]
    }
    
    print("📤 Testing SMA strategy via FastAPI...")
    response = client.post("/run", json=payload)
    
    print(f"📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SMA API test successful!")
        print(f"   Final Value: {data['summary']['final_value']}")
        return True
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"   Details: {response.text}")
        return False

if __name__ == "__main__":
    success1 = test_simple_api()
    success2 = test_with_sma_strategy()
    
    print(f"\n{'='*50}")
    print(f"Simple Test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"SMA Test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("🎉 All simple API tests passed!")
    else:
        print("❌ Some tests failed.")