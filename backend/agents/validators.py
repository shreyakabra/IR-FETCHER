from ..models import FoundFile
from ..util.text import guess_year_from_title
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

DOC_TYPE_KEYWORDS: Dict[str, tuple] = {
    "annual report": (
        "annual report",
        "annual-report",
        "annual results",
        "form 10-k",
        "10-k",
        "10k",
        "annual disclosure",
    ),
    "earnings release": (
        "earnings release",
        "quarterly results",
        "quarterly report",
        "results release",
        "press release",
        "trading update",
        "investor update",
        "q1 results",
        "q2 results",
        "q3 results",
        "q4 results",
        "semi-annual",
        "half-year",
    ),
    "investor presentation": (
        "investor presentation",
        "investor deck",
        "earnings presentation",
        "slide deck",
        "investor slides",
        "investor day",
    ),
    "financial statements": (
        "financial statements",
        "financial statement",
        "financial results",
        "balance sheet",
        "income statement",
        "cash flow statement",
        "statement of profit",
    ),
    "10-k": (
        "form 10-k",
        "10-k",
        "10k",
    ),
    "10-q": (
        "form 10-q",
        "10-q",
        "10q",
    ),
    "20-f": (
        "20-f",
        "form 20-f",
    ),
}

PERIOD_KEYWORDS: Dict[str, tuple] = {
    "Q1": ("q1", "first quarter", "1st quarter", "quarter 1"),
    "Q2": ("q2", "second quarter", "2nd quarter", "quarter 2"),
    "Q3": ("q3", "third quarter", "3rd quarter", "quarter 3"),
    "Q4": ("q4", "fourth quarter", "4th quarter", "quarter 4"),
    "H1": ("h1", "first half", "1st half", "half-year", "semi-annual"),
    "H2": ("h2", "second half", "2nd half", "half-year"),
}

def acceptable_mime(mt: Optional[str], url: str = "") -> bool:
    # If mimetype is None, check URL for PDF extension
    if not mt:
        # Accept if URL looks like a PDF or document
        if url.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv')):
            return True
        # Also accept if URL contains common document patterns
        if any(term in url.lower() for term in ['/pdf/', '/document/', '/report/', '/annual', '/10-k', '/10k']):
            return True
        return False

    mt = mt.lower()
    return any([
        mt.startswith("application/pdf"),
        mt.endswith("msword"),
        "officedocument" in mt,
        mt.startswith("text/csv"),
        mt.startswith("application/vnd.ms-excel"),
        "pdf" in mt,
    ])

def _matches_doc_type(doc_type: str, title: str, url: str) -> bool:
    tokens = DOC_TYPE_KEYWORDS.get(doc_type.lower())
    if not tokens:
        return True
    text = f"{title} {url}".lower()
    return any(token in text for token in tokens)

def _matches_period(extras: Dict[str, str], title: str, url: str) -> bool:
    if not extras:
        return True
    text = f"{title} {url}".lower()
    quarter = extras.get("quarter")
    if quarter:
        keywords = PERIOD_KEYWORDS.get(quarter, ())
        if not any(k in text for k in keywords):
            return False
    half = extras.get("half")
    if half:
        keywords = PERIOD_KEYWORDS.get(half, ())
        if not any(k in text for k in keywords):
            return False
    return True

def validate_found(f: FoundFile, doc_type: str, extras: Dict[str, str], wanted_years):
    # Check if URL or mimetype suggests it's a document
    ok_mime = acceptable_mime(f.mimetype, f.url)

    ok_year = True
    if wanted_years:
        y = f.year or guess_year_from_title(f.title) or guess_year_from_title(f.url)
        if y:
            ok_year = (y in wanted_years)
        else:
            ok_year = False  # reject if we cannot determine the year when a specific year was requested

    ok_type = _matches_doc_type(doc_type, f.title, f.url)
    ok_period = _matches_period(extras, f.title, f.url)

    result = ok_mime and ok_year and ok_type and ok_period
    if not result:
        logger.debug(
            "Filtered out: %s (mime_ok=%s, year_ok=%s, type_ok=%s, period_ok=%s)",
            f.url,
            ok_mime,
            ok_year,
            ok_type,
            ok_period,
        )
    return result
