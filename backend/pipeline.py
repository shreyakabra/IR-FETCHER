from typing import List, Optional
from datetime import datetime
import re
import logging
from copy import deepcopy
from .models import DownloadRequest, DownloadResponse, FoundFile, DownloadedFile, Intent
from .agents.parser import parse_prompt
from .agents.search_router import route_search
from .agents.validators import validate_found
from .services.downloader import download_one
from .services.metadata import write_metadata
from .services.ticker import resolve_company_from_ticker
from .util.text import guess_year_from_title

logger = logging.getLogger(__name__)

def _years_from_window(window: int) -> List[int]:
    """Return a list of years representing the last `window` completed years."""
    current_year = datetime.utcnow().year - 1
    return [current_year - i for i in range(window)]

def _normalize(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r"[^a-z0-9]", "", text.lower())

def _tokenize_company(name: Optional[str]) -> List[str]:
    return [
        t for t in (_normalize(tok) for tok in re.split(r"\s+", name or ""))
        if len(t) > 2
    ]

def _matches_company(found: FoundFile, preferred: Optional[str], original: Optional[str], ticker: Optional[str]) -> bool:
    haystack = " ".join(filter(None, [found.title, found.url]))
    hay_norm = _normalize(haystack)

    # If ticker provided, require ticker match OR strong company name match
    ticker_norm = _normalize(ticker) if ticker else None
    if ticker_norm:
        if ticker_norm in hay_norm:
            return True
        # Require at least 2 significant company tokens to match
        preferred_tokens = _tokenize_company(preferred)
        original_tokens = _tokenize_company(original)
        all_tokens = list(set(preferred_tokens + original_tokens))
        if len(all_tokens) >= 2:
            matches = sum(1 for tok in all_tokens if tok and tok in hay_norm)
            if matches >= 2:
                return True
        # Single long token match (for single-word companies)
        if all_tokens and len(all_tokens[0]) >= 5:
            if all_tokens[0] in hay_norm:
                return True
        return False

    # No ticker: require company name match
    preferred_tokens = _tokenize_company(preferred)
    original_tokens = _tokenize_company(original)
    all_tokens = list(set(preferred_tokens + original_tokens))
    
    if not all_tokens:
        return True  # No company specified, accept all
    
    # Require at least one significant token match
    return any(tok and len(tok) >= 3 and tok in hay_norm for tok in all_tokens)

def _infer_year(f: FoundFile) -> Optional[int]:
    return f.year or guess_year_from_title(f.title) or guess_year_from_title(f.url)

def _select_best_matches(files: List[FoundFile], years: List[int]) -> List[FoundFile]:
    if not files:
        return []

    selected: List[FoundFile] = []
    used = set()

    if years:
        for target_year in years:
            for idx, f in enumerate(files):
                if idx in used:
                    continue
                y = _infer_year(f)
                if y == target_year:
                    selected.append(f)
                    used.add(idx)
                    break
        return selected

    # If no year specified, only return the top match
    return files[:1]

async def run_pipeline(req: DownloadRequest) -> DownloadResponse:
    base_intent = parse_prompt(req.prompt)
    logger.info(f"Processing request: {req.prompt} -> {base_intent}")

    doc_types = base_intent.doc_types or [base_intent.doc_type]
    aggregated_results: List[DownloadedFile] = []

    for doc_type in doc_types:
        current_intent = Intent(
            company=base_intent.company,
            doc_type=doc_type,
            years=list(base_intent.years),
            region=base_intent.region,
            doc_types=doc_types,
            extras=deepcopy(base_intent.extras),
        )
        results = await _run_single_intent(req, current_intent)
        aggregated_results.extend(results)

    base_intent.doc_type = doc_types[0]
    base_intent.doc_types = doc_types
    return DownloadResponse(intent=base_intent, results=aggregated_results)

async def _run_single_intent(req: DownloadRequest, intent: Intent) -> List[DownloadedFile]:
    parsed_company = intent.company

    if req.ticker:
        resolved_name = resolve_company_from_ticker(req.ticker)
        intent.extras["ticker"] = req.ticker.upper()
        intent.extras["parsed_company"] = parsed_company
        if resolved_name:
            intent.company = resolved_name
            logger.info(f"Resolved ticker {req.ticker} to company {resolved_name}")
        else:
            logger.warning(f"Unable to resolve ticker {req.ticker}, falling back to parsed company {intent.company}")

    if req.year_window and req.year_window > 0:
        target_years = _years_from_window(req.year_window)
        intent.years = target_years
        logger.info(f"Applying year window ({req.year_window}): {target_years}")

    logger.info(f"Searching for {intent.company} / {intent.doc_type} / years {intent.years}")
    found: List[FoundFile] = await route_search(intent)
    logger.info(f"Found {len(found)} files for {intent.doc_type}")

    ticker_code = intent.extras.get("ticker")
    company_filtered = [
        f for f in found
        if _matches_company(f, intent.company, parsed_company, ticker_code)
    ]
    if req.ticker:
        found = company_filtered
        logger.info(f"Ticker provided; {len(found)} results match company/ticker filter")
    elif company_filtered:
        logger.info(f"Company filter retained {len(company_filtered)} results")
        found = company_filtered
    else:
        logger.info("Company filter removed all results; using unfiltered list")

    filtered = [f for f in found if validate_found(f, intent.doc_type, intent.extras, intent.years)]

    filtered = _select_best_matches(filtered, intent.years if intent.years else [])

    logger.info(f"Filtered to {len(filtered)} files for {intent.doc_type}")

    results: List[DownloadedFile] = []
    for f in filtered:
        default_year = intent.years[0] if intent.years else None
        df = await download_one(intent.company, intent.doc_type, (f.year or default_year), f)
        if df:
            write_metadata(df)
            results.append(df)
        else:
            logger.warning(f"Download failed for {f.url}")

    logger.info(f"Successfully downloaded {len(results)} files for {intent.doc_type}")
    return results
