import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"


def _extract_name(quote: dict) -> Optional[str]:
    return (
        quote.get("shortname")
        or quote.get("longname")
        or quote.get("name")
        or quote.get("displayName")
    )


def resolve_company_from_ticker(ticker: str) -> Optional[str]:
    """
    Resolve a ticker (e.g., AAPL) to its company name using Yahoo Finance's public search endpoint.
    Falls back to None if the lookup fails.
    """
    if not ticker:
        return None

    symbol = ticker.strip().upper()
    if not symbol:
        return None

    try:
        resp = requests.get(
            YAHOO_SEARCH_URL,
            params={"q": symbol, "quotesCount": 10, "newsCount": 0, "lang": "en-US", "region": "US"},
            timeout=5,
            headers={"User-Agent": "IR-Downloader/1.0"},
        )
        resp.raise_for_status()
        data = resp.json()
        quotes = data.get("quotes", [])
        for quote in quotes:
            q_symbol = (quote.get("symbol") or "").upper()
            base_symbol = q_symbol.split(".")[0]
            if q_symbol == symbol or base_symbol == symbol:
                resolved = _extract_name(quote)
                if resolved:
                    return resolved
        if quotes:
            fallback = _extract_name(quotes[0])
            if fallback:
                return fallback
    except Exception as exc:
        logger.warning("Failed to resolve ticker %s: %s", symbol, exc)
    return None

