from typing import Dict, Any, List, Optional
import os
import backtrader as bt
from src.utils.datafeed import bars_to_temp_csv

class EquityCurve(bt.Analyzer):
    """Analyzer that records portfolio value per bar for equity_curve output."""
    def start(self): self._data = []
    def next(self):
        dt = self.strategy.datas[0].datetime.date(0).strftime("%Y-%m-%d")
        self._data.append({"time": dt, "value": float(self.strategy.broker.getvalue())})
    def get_analysis(self): return self._data

class TradeCaptureMixin(bt.Strategy):
    """Mixin to collect closed trades in notify_trade for API output."""
    def __init__(self): super().__init__(); self._trades = []
    def notify_trade(self, trade):
        if trade.isclosed:
            entry = bt.num2date(trade.dtopen).strftime("%Y-%m-%d")
            exit_  = bt.num2date(trade.dtclose).strftime("%Y-%m-%d")
            # Determine direction based on trade size (positive = long, negative = short)
            direction = "long" if trade.size > 0 else "short"
            self._trades.append({
                "entry_time": entry, "exit_time": exit_,
                "direction": direction,
                "pnl": float(trade.pnl), "pnlcomm": float(trade.pnlcomm)
            })

def _load_strategy_class(code: str) -> type:
    """
    Compile and return the first subclass of bt.Strategy from a code string.
    Raises RuntimeError if none found.
    """
    ns: Dict[str, Any] = {}
    # Use a more permissive globals for strategy execution
    # In production, you might want to restrict this more
    safe_globals = {
        "__builtins__": __builtins__,
        "backtrader": bt,
        "bt": bt
    }
    exec(code, safe_globals, ns)
    for v in ns.values():
        if isinstance(v, type) and issubclass(v, bt.Strategy):
            return v
    raise RuntimeError("No bt.Strategy subclass found in code")

def run_backtest(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Backtrader on provided bars with a dynamic strategy.
    Inputs:
      payload['code']: Python bt.Strategy class as string
      payload['bars']: list of OHLCV dicts (YYYY-MM-DD dates)
      payload['capital']: initial cash (float)
      payload['params']: dict passed to strategy
    Returns:
      dict with keys: ohlcv, trades, equity_curve, summary
    """
    code: str = payload["code"]
    bars: Optional[List[Dict[str, Any]]] = payload.get("bars")
    if not bars:
        raise RuntimeError("MVP requires 'bars' in payload")

    capital: float = float(payload.get("capital", 10000))
    params: Dict[str, Any] = payload.get("params", {})

    # Build Cerebro
    cerebro = bt.Cerebro()

    # Strategy with trade capture
    user_cls = _load_strategy_class(code)
    Strat = type("UserStrategyWithCapture", (TradeCaptureMixin, user_cls), {})
    cerebro.addstrategy(Strat, **params)

    # Data feed via temp CSV
    path = bars_to_temp_csv(bars)
    data = bt.feeds.GenericCSVData(
        dataname=path, dtformat="%Y-%m-%d",
        datetime=0, open=1, high=2, low=3, close=4, volume=5, openinterest=6
    )
    cerebro.adddata(data, name=payload.get("symbol") or "DATA")

    # Broker and analyzers
    cerebro.broker.setcash(capital)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="tradesum")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe", timeframe=bt.TimeFrame.Days, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(EquityCurve, _name="equity")

    try:
        res = cerebro.run()
        strat = res[0]

        ta = strat.analyzers.tradesum.get_analysis()
        dd = strat.analyzers.dd.get_analysis()
        sh = strat.analyzers.sharpe.get_analysis()

        total_trades = ta.get("total", {}).get("total", 0)
        won = ta.get("won", {}).get("total", 0)
        win_rate = float(won) / total_trades if total_trades else 0.0

        final_value = float(cerebro.broker.getvalue())
        summary = {
            "final_value": round(final_value, 6),
            "return_pct": round((final_value / capital - 1.0) * 100.0, 6),
            "total_trades": int(total_trades),
            "win_rate": round(win_rate, 6),
            "max_drawdown_pct": round(dd.get("max", {}).get("drawdown", 0.0), 6),
            "sharpe": float(sh.get("sharperatio") or 0.0)
        }

        return {
            "ohlcv": bars,
            "trades": getattr(strat, "_trades", []),
            "equity_curve": strat.analyzers.equity.get_analysis(),
            "summary": summary
        }
    finally:
        try: os.remove(path)
        except Exception: pass