from __future__ import annotations

from typing import Optional
from math import exp


def _normalize_positive(value: Optional[float], scale: float) -> float:
    """
    Turn a positive value into 0–1 where:
      small value -> near 1 (risky)
      large value -> near 0 (safe)

    Using exp(-value/scale).
    """
    if value is None or value <= 0:
        return 1.0
    return float(exp(-value / scale))


def compute_liquidity_score(pool_liquidity_usd: Optional[float]) -> float:
    # $500k is "reasonably safe"; below that grows risky
    return _normalize_positive(pool_liquidity_usd, scale=500_000)


def compute_volume_score(volume_24h_usd: Optional[float]) -> float:
    # $1M daily volume typical threshold
    return _normalize_positive(volume_24h_usd, scale= 5_000_000)


def compute_volatility_score(volatility_24h: Optional[float]) -> float:
    """
    volatility_24h is absolute percent change.
    Higher => more risky.
    Map: 0% -> 0 risk, 20%+ -> near max risk.
    """
    if volatility_24h is None:
        return 1.0
    if volatility_24h < 0:
        volatility_24h = abs(volatility_24h)
    # scale=20 means 20% = high risk
    return min(volatility_24h / 20.0, 1.0)


def compute_overall_risk_score(
    liq: float, vol: float, volat: float
) -> float:
    """
    Weighted average.
    Liquidity and volume matter more than volatility.
    """
    return float(0.4 * liq + 0.4 * vol + 0.2 * volat)
