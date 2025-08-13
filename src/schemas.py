from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Bar(BaseModel):
    """Single OHLCV bar used as input/output. time is YYYY-MM-DD."""
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    openinterest: Optional[float] = 0.0

class RunRequest(BaseModel):
    """Input payload to /run (MVP requires bars)."""
    code: str = Field(..., description="Python bt.Strategy subclass as string")
    bars: Optional[List[Bar]] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = "1d"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    capital: float = 10000
    params: Dict[str, Any] = {}
    risk: Dict[str, Any] = {}

class TradeOut(BaseModel):
    """Closed trade summary emitted by strategy capture."""
    entry_time: str
    exit_time: str
    direction: str
    pnl: float
    pnlcomm: float

class EquityPoint(BaseModel):
    """Portfolio value at each bar."""
    time: str
    value: float

class SummaryOut(BaseModel):
    """Aggregate metrics calculated after run."""
    final_value: float
    return_pct: float
    total_trades: int
    win_rate: float
    max_drawdown_pct: float
    sharpe: float

class RunResponse(BaseModel):
    """BacktestResults output shape (ohlcv, trades, equity_curve, summary)."""
    ohlcv: List[Bar]
    trades: List[TradeOut]
    equity_curve: List[EquityPoint]
    summary: SummaryOut