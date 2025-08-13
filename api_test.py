#!/usr/bin/env python3
"""
Direct API test using the FastAPI TestClient
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_api_endpoint():
    """Test the /run endpoint directly"""
    print("Testing FastAPI /run endpoint...")
    
    payload = {
        "code": """
import backtrader as bt
class SimpleStrategy(bt.Strategy):
    params = (('stake', 100),)
    
    def __init__(self):
        self.sma = bt.ind.SMA(self.data.close, period=5)
        
    def next(self):
        if not self.position and len(self.data) > 10:
            self.buy(size=self.p.stake)
        elif self.position and len(self.data) > 15:
            self.sell(size=self.p.stake)
        """,
        "capital": 100000,
        "params": {"stake": 50},
        "bars": [
            {"time": f"2020-01-{i:02d}", "open": 100+i*0.5, "high": 101+i*0.5, "low": 99+i*0.5, 
             "close": 100.5+i*0.5, "volume": 10000+i*100, "openinterest": 0}
            for i in range(2, 32)  # 30 bars
        ]
    }
    
    print(f"📤 Sending request with {len(payload['bars'])} bars...")
    
    response = client.post("/run", json=payload)
    
    print(f"📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response successful!")
        print(f"   📊 Final Value: ${data['summary']['final_value']:,.2f}")
        print(f"   📈 Return: {data['summary']['return_pct']:.2f}%")
        print(f"   🔄 Total Trades: {data['summary']['total_trades']}")
        print(f"   📉 Equity Points: {len(data['equity_curve'])}")
        print(f"   📋 OHLCV Records: {len(data['ohlcv'])}")
        
        if data['trades']:
            print(f"   💰 Sample Trade: {data['trades'][0]}")
        
        return True
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"   Details: {response.text}")
        return False

def test_error_cases():
    """Test error handling"""
    print("\nTesting error cases...")
    
    # Test missing code
    response = client.post("/run", json={"bars": []})
    print(f"Missing code test: {response.status_code} (expected 400)")
    
    # Test symbol-only (should return 501)
    response = client.post("/run", json={
        "code": "import backtrader as bt\nclass S(bt.Strategy): pass",
        "symbol": "AAPL",
        "start_date": "2020-01-01",
        "end_date": "2020-01-31"
    })
    print(f"Symbol-only test: {response.status_code} (expected 501)")

def main():
    print("🧪 Backtrader Service API Test")
    print("=" * 50)
    
    success = test_api_endpoint()
    test_error_cases()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 API tests completed successfully!")
        print("The Backtrader Service REST API is working correctly.")
        return 0
    else:
        print("❌ API tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())