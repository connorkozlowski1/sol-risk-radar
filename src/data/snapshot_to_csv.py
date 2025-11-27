from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import datetime, timezone
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
TOKENS_FILE = Path("tokens.txt")


def ensure_processed_dir() -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_tokens(path: Path = TOKENS_FILE) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Token list file not found: {path}")

    tokens: List[str] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        addr = line.split()[0]
        tokens.append(addr)

    if not tokens:
        raise ValueError(f"No tokens found in {path}")

    return tokens


def write_snapshots(token_addresses: List[str]) -> None:
    ensure_processed_dir()

    snapshot_time = datetime.now(timezone.utc).isoformat()

    records = []
    for addr in token_addresses:
        rec = build_token_risk_record_from_dexscreener(addr)
        if rec is None:
            continue

        liq_score = compute_liquidity_score(rec.pool_liquidity_usd)
        vol_score = compute_volume_score(rec.volume_24h_usd)
        vola_score = compute_volatility_score(rec.volatility_24h)
        overall = compute_overall_risk_score(liq_score, vol_score, vola_score)

        rec.liquidity_score = liq_score
        rec.volume_score = vol_score
        rec.concentration_score = None
        rec.volatility_score = vola_score
        rec.overall_risk_score = overall

        row = asdict(rec)
        row["snapshot_time_utc"] = snapshot_time
        records.append(row)

    if not records:
        print("No records to write.")
        return

    fieldnames = list(records[0].keys())
    file_exists = SNAPSHOT_CSV.exists()

    with SNAPSHOT_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(records)

    print(f"Appended {len(records)} records to {SNAPSHOT_CSV}")


def main() -> None:
    tokens = load_tokens()
    write_snapshots(tokens)


if __name__ == "__main__":
    main()
