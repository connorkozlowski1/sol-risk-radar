from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .schema import TokenRiskRecord
from .dexscreener_client import get_token_pairs_solana

logger = logging.getLogger(__name__)


def _pick_primary_pair(pairs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Heuristic: choose the pair with the highest USD liquidity.
    """
    if not pairs:
        return None

    def liquidity_usd(p: Dict[str, Any]) -> float:
        liq = p.get("liquidity") or {}
        return float(liq.get("usd") or 0.0)

    return max(pairs, key=liquidity_usd)


def _ms_to_datetime(ms: Optional[int]) -> Optional[datetime]:
    if ms is None:
        return None
    try:
        return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
    except Exception:
        return None


def build_token_risk_record_from_dexscreener(token_address: str) -> Optional[TokenRiskRecord]:
    """
    Build a TokenRiskRecord for a Solana token using Dexscreener data only.

    For now, we fill:
      - token_address, symbol, name
      - created_at (from pairCreatedAt)
      - pool_liquidity_usd
      - volume_24h_usd
      - price_current_usd
      - simple volatility proxy from priceChange.h24

    All other fields remain None. We'll enrich them later with more data sources.
    """
    pairs = get_token_pairs_solana(token_address)
    if not pairs:
        logger.warning("No pairs found on Dexscreener for token %s", token_address)
        return None

    pair = _pick_primary_pair(pairs)
    if pair is None:
        logger.warning("Failed to pick primary pair for token %s", token_address)
        return None

    base = pair.get("baseToken") or {}
    symbol = base.get("symbol")
    name = base.get("name")

    price_usd = pair.get("priceUsd")
    try:
        price_current_usd = float(price_usd) if price_usd is not None else None
    except Exception:
        price_current_usd = None

    liq = pair.get("liquidity") or {}
    try:
        pool_liquidity_usd = float(liq.get("usd")) if liq.get("usd") is not None else None
    except Exception:
        pool_liquidity_usd = None

    vol = pair.get("volume") or {}
    try:
        volume_24h_usd = float(vol.get("h24")) if vol.get("h24") is not None else None
    except Exception:
        volume_24h_usd = None

    pc = pair.get("priceChange") or {}
    # treat absolute h24 % move as a naive volatility proxy for now
    try:
        volatility_24h = abs(float(pc.get("h24"))) if pc.get("h24") is not None else None
    except Exception:
        volatility_24h = None

    created_at = _ms_to_datetime(pair.get("pairCreatedAt"))

    record = TokenRiskRecord(
        token_address=token_address,
        symbol=symbol,
        name=name,
        created_at=created_at,
        first_trade_at=created_at,  # best proxy for now

        # holder concentration – not available yet from Dexscreener
        top1_share=None,
        top5_share=None,
        top10_share=None,
        gini_index=None,
        herfindahl_index=None,

        # liquidity + volume
        pool_liquidity_usd=pool_liquidity_usd,
        pool_token_reserve=None,
        pool_sol_reserve=None,
        volume_24h_usd=volume_24h_usd,

        # price/volatility
        price_current_usd=price_current_usd,
        volatility_1h=None,
        volatility_24h=volatility_24h,

        # derived risk scores – to be computed later
        concentration_score=None,
        liquidity_score=None,
        volatility_score=None,
        overall_risk_score=None,
    )

    return record


def main() -> None:
    """
    Manual smoke test using WSOL.
    """
    # Wrapped SOL
    wsol = "So11111111111111111111111111111111111111112"

    rec = build_token_risk_record_from_dexscreener(wsol)
    if rec is None:
        print("No record built for WSOL")
        return

    print("WSOL TokenRiskRecord snapshot:")
    for k, v in asdict(rec).items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
