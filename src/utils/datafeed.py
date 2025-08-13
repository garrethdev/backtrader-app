import csv, tempfile
from typing import List, Dict, Any

def bars_to_temp_csv(bars: List[Dict[str, Any]]) -> str:
    """
    Write bars to a temp CSV compatible with backtrader GenericCSVData.
    Returns path to the temp file. Caller is responsible for cleanup.

    CSV columns: datetime,open,high,low,close,volume,openinterest
    datetime format: YYYY-MM-DD
    """
    tmp = tempfile.NamedTemporaryFile(mode="w+", newline="", suffix=".csv", delete=False)
    w = csv.writer(tmp)
    w.writerow(["datetime","open","high","low","close","volume","openinterest"])
    for r in bars:
        w.writerow([r["time"], r["open"], r["high"], r["low"], r["close"], r["volume"], r.get("openinterest", 0)])
    tmp.flush()
    tmp.close()
    return tmp.name