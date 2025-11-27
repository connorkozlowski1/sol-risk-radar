from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TokenRiskRecord:
    token_address: str
    symbol: Optional[str]
    name: Optional[str]

    created_at: Optional[datetime]
    first_trade_at: Optional[datetime]

    # holder concentration
    top1_share: Optional[float]
    top5_share: Optional[float]
    top10_share: Optional[float]
    gini_index: Optional[float]
    herfindahl_index: Optional[float]

    # liquidity + volume
    pool_liquidity_usd: Optional[float]
    pool_token_reserve: Optional[float]
    pool_sol_reserve: Optional[float]
    volume_24h_usd: Optional[float]

    # price/volatility
    price_current_usd: Optional[float]
    volatility_1h: Optional[float]
    volatility_24h: Optional[float]

    # derived risk scores
    concentration_score: Optional[float]
    liquidity_score: Optional[float]
    volatility_score: Optional[float]
    overall_risk_score: Optional[float]
