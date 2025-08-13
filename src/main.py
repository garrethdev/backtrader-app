from fastapi import FastAPI, HTTPException
from src.schemas import RunRequest, RunResponse
from src.runner import run_backtest

app = FastAPI(title="Backtrader Service")

@app.post("/run", response_model=RunResponse, tags=["backtest"])
def run(req: RunRequest):
    """
    Execute a backtest. MVP requires `bars` in request.
    If only symbol+dates are provided, return 501 (future extension).
    """
    if not req.code:
        raise HTTPException(400, "code is required")
    if not req.bars and not (req.symbol and req.start_date and req.end_date):
        raise HTTPException(400, "Provide bars or symbol with start_date and end_date")
    if not req.bars:
        raise HTTPException(501, "symbol-based data loading not implemented in MVP")
    try:
        return run_backtest(req.model_dump())
    except Exception as e:
        raise HTTPException(500, str(e))