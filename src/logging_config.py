import logging
import hashlib
from typing import Any

def setup_logging():
    """Setup basic logging configuration for the service."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_code_hash(code: str) -> str:
    """
    Generate and log a hash of the strategy code for debugging purposes.
    Returns the hash for reference.
    """
    code_hash = hashlib.sha256(code.encode()).hexdigest()[:8]
    logger = logging.getLogger(__name__)
    logger.info(f"Processing strategy with code hash: {code_hash}")
    return code_hash

def log_request_summary(payload: dict[str, Any]) -> None:
    """Log a summary of the backtest request without exposing sensitive data."""
    logger = logging.getLogger(__name__)
    
    bars_count = len(payload.get("bars", []))
    symbol = payload.get("symbol", "UNKNOWN")
    capital = payload.get("capital", 0)
    params_count = len(payload.get("params", {}))
    
    logger.info(f"Backtest request: symbol={symbol}, bars={bars_count}, capital={capital}, params={params_count}")
    
    if payload.get("code"):
        log_code_hash(payload["code"])