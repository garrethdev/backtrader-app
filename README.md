# Backtrader Service

FastAPI microservice for executing trading strategy backtests. Send Python strategy code + market data → get back trades, equity curve, and performance metrics.

## Setup & Run

```bash
cd backtrader-service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --host 127.0.0.1 --port 8080
```

**Test:** `python3 validate.py` or visit http://127.0.0.1:8080/docs

## API Usage

**POST /run** - Execute backtest

**Request:**
```json
{
  "code": "import backtrader as bt\nclass MyStrategy(bt.Strategy):\n  def __init__(self): self.sma = bt.ind.SMA(period=20)\n  def next(self):\n    if not self.position: self.buy()",
  "bars": [{"time": "2020-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 1000, "openinterest": 0}],
  "capital": 10000,
  "params": {"period": 20}
}
```

**Response:**
```json
{
  "trades": [{"entry_time": "2020-01-02", "exit_time": "2020-01-03", "direction": "long", "pnl": 50.0}],
  "equity_curve": [{"time": "2020-01-02", "value": 10000.0}],
  "summary": {"final_value": 10050.0, "return_pct": 0.5, "total_trades": 1, "win_rate": 1.0, "sharpe": 0.75}
}
```

## Strategy Code Requirements

Must inherit from `bt.Strategy` and implement `__init__()` + `next()`:

```python
import backtrader as bt

class SMACross(bt.Strategy):
    params = (('fast', 10), ('slow', 20))
    
    def __init__(self):
        self.fast = bt.ind.SMA(period=self.p.fast)
        self.slow = bt.ind.SMA(period=self.p.slow)
    
    def next(self):
        if not self.position and self.fast > self.slow:
            self.buy()
        elif self.position and self.fast < self.slow:
            self.close()
```

## Key Details

- **Data**: Requires `bars` array (OHLCV). Symbol-based fetching returns 501 (MVP limitation)
- **Indicators**: Ensure enough bars for your indicators (SMA(20) needs 20+ bars)
- **Parameters**: Override strategy params via `"params": {"period": 30}`
- **Docker**: `docker build -t backtrader-service . && docker run -p 8080:8080 backtrader-service`

## Troubleshooting

- **"array assignment index out of range"** → Not enough bars for indicators
- **"No bt.Strategy subclass found"** → Code must contain valid strategy class
- **422 errors** → Missing required fields or invalid JSON

**Testing:** `python3 sample_test.py` for working examples