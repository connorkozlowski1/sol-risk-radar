from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.dexscreener.com"


class DexscreenerError(RuntimeError):
    pass


def _get(path: str) -> Any:
    """
    Low-level GET helper for Dexscreener public API.
    No auth or API key required.
    """
    url = f"{BASE_URL}{path}"
    headers = {"accept": "application/json"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as exc:
        raise DexscreenerError(f"Request to {url} failed: {exc}") from exc

    if resp.status_code != 200:
        raise DexscreenerError(f"Dexscreener returned {resp.status_code}: {resp.text[:200]}")

    try:
        return resp.json()
    except ValueError as exc:
        raise DexscreenerError(f"Failed to parse JSON from {url}: {resp.text[:200]}") from exc


def get_token_pairs_solana(token_address: str) -> List[Dict[str, Any]]:
    """
    Get all pools/pairs for a given Solana token.

    Endpoint:
      GET /tokens/v1/{chainId}/{tokenAddresses}

    For us:
      chainId = "solana"
      tokenAddresses = single address
    """
    data = _get(f"/tokens/v1/solana/{token_address}")

    if not isinstance(data, list):
        raise DexscreenerError(f"Unexpected /tokens response type: {type(data)}")

    return data


def main() -> None:
    """
    Manual smoke test using WSOL.
    """
    # Wrapped SOL token address
    wsol = "So11111111111111111111111111111111111111112"
    pairs = get_token_pairs_solana(wsol)

    print(f"Found {len(pairs)} WSOL pairs on Dexscreener")
    if not pairs:
        return

    first = pairs[0]
    print("First pair keys:", sorted(first.keys()))

    # Show a few key risk-related fields if present
    for key in [
        "dexId",
        "pairAddress",
        "priceUsd",
        "fdv",
        "marketCap",
        "pairCreatedAt",
    ]:
        if key in first:
            print(f"{key}: {first[key]}")

    if "liquidity" in first:
        print("liquidity:", first["liquidity"])
    if "volume" in first:
        print("volume:", first["volume"])
    if "priceChange" in first:
        print("priceChange:", first["priceChange"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
