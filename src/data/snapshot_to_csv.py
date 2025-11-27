from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from typing import List

from .token_snapshot import build_token_risk_record_from_dexscreener
from src.models.risk_scoring import (
    compute_liquidity_score,
    compute_volume_score,
    compute_volatility_score,
    compute_overall_risk_score,
)


DATA_PROCESSED_DIR = Path("data/processed")
SNAPSHOT_CSV = DATA_PROCESSED_DIR / "token_snapshots.csv"


def ensure_processed_dir() -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def write_snapshots(token_addresses: List[str]) -> None:
    ensure_processed_dir()

    records = []
    for addr in token_addresses:
        rec = build_token_risk_record_from_dexscreener(addr)
        if rec is None:
            continue

        # compute risk component scores
        liq_score = compute_liquidity_score(rec.pool_liquidity_usd)
        vol_score = compute_volume_score(rec.volume_24h_usd)
        vola_score = compute_volatility_score(rec.volatility_24h)
        overall = compute_overall_risk_score(liq_score, vol_score, vola_score)

        # assign into the record
        rec.liquidity_score = liq_score
        rec.volume_score = vol_score
        rec.concentration_score = None  # future
        rec.volatility_score = vola_score
        rec.overall_risk_score = overall

        records.append(asdict(rec))

    if not records:
        print("No records to write.")
        return

    fieldnames = list(records[0].keys())

    with SNAPSHOT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} records to {SNAPSHOT_CSV}")


def main() -> None:
    # For now, just WSOL as a smoke test
    tokens = [
        "So11111111111111111111111111111111111111112",  # WSOL
    ]
    write_snapshots(tokens)


if __name__ == "__main__":
    main()
