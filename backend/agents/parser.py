from ..models import Intent
import re
from typing import List

ALL_DOC_TYPES = [
    "annual report",
    "earnings release",          # quarterly / half-yearly / semi-annual reports
    "investor presentation",     # presentations / slide decks
    "financial statements",      # full financial statements
]

DEFAULT_DOC_TYPES = ["annual report"]

QUARTER_PATTERNS = {
    "Q1": [
        r"\bq1\b",
        r"\bq 1\b",
        r"first quarter",
        r"1st quarter",
        r"quarter one",
    ],
    "Q2": [
        r"\bq2\b",
        r"\bq 2\b",
        r"second quarter",
        r"2nd quarter",
        r"quarter two",
    ],
    "Q3": [
        r"\bq3\b",
        r"\bq 3\b",
        r"third quarter",
        r"3rd quarter",
        r"quarter three",
    ],
    "Q4": [
        r"\bq4\b",
        r"\bq 4\b",
        r"fourth quarter",
        r"4th quarter",
        r"quarter four",
        r"year-end quarter",
    ],
}

HALF_PATTERNS = {
    "H1": [
        r"\bh1\b",
        r"first half",
        r"1st half",
        r"half-year",
        r"semi-annual",
        r"semiannual",
    ],
    "H2": [
        r"\bh2\b",
        r"second half",
        r"2nd half",
        r"h2 fy",
        r"h2fy",
    ],
}

def _extract_years(text: str) -> List[int]:
    """
    Extract explicit years from the text.
    - For ranges like "2022-23" or "2022-2023", treat this as the END year (2023).
    - For ranges like "2020 to 2024", also use the END year (2024).
    - Otherwise, return the list of distinct years found.
    """
    m = re.search(r"(20\d{2})\s*(?:to|-|–|—)\s*(\d{2,4})", text)
    if m:
        start = int(m.group(1))
        end_raw = m.group(2)
        if len(end_raw) == 2:
            end = int(str(start)[:2] + end_raw)
        else:
            end = int(end_raw)
        years = sorted({start, end})
        return years

    years = sorted({int(y) for y in re.findall(r"(20\d{2})", text)})
    return years or []

def _detect_periods(text: str):
    extras = {}
    txt = text.lower()
    for code, patterns in QUARTER_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, txt):
                extras["quarter"] = code
                return extras
    for code, patterns in HALF_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, txt):
                extras["half"] = code
                return extras
    return extras

def _extract_doc_types(text: str) -> List[str]:
    txt = text.lower()

    # "All reports" should include every major document bucket
    if any(phrase in txt for phrase in ["all report", "all reports", "all filings", "all documents", "all docs"]):
        return ALL_DOC_TYPES.copy()

    mapping = [
        ("annual report", "annual report"),
        ("annual", "annual report"),
        ("form 10-k", "10-K"),
        ("10-k", "10-K"),
        ("10k", "10-K"),
        ("10-q", "10-Q"),
        ("10q", "10-Q"),
        ("20-f", "20-F"),
        ("financial statement", "financial statements"),
        ("full financial", "financial statements"),
        ("balance sheet", "financial statements"),
        ("income statement", "financial statements"),
        ("cash flow", "financial statements"),
        ("investor presentation", "investor presentation"),
        ("investor deck", "investor presentation"),
        ("slide deck", "investor presentation"),
        ("investor slide deck", "investor presentation"),
        ("presentation deck", "investor presentation"),
        ("earnings presentation", "investor presentation"),
        ("earnings release", "earnings release"),
        ("quarterly report", "earnings release"),
        ("quarterly results", "earnings release"),
        ("half-year", "earnings release"),
        ("semi-annual", "earnings release"),
        ("quarterly", "earnings release"),
        ("results release", "earnings release"),
    ]

    doc_types: List[str] = []
    for needle, normalized in mapping:
        if needle in txt and normalized not in doc_types:
            doc_types.append(normalized)

    if not doc_types:
        doc_types = DEFAULT_DOC_TYPES.copy()
    return doc_types

def parse_prompt(prompt: str) -> Intent:
    t = prompt.strip()

    doc_types = _extract_doc_types(t)
    doc_type = doc_types[0]

    tokens = [w for w in re.findall(r"[A-Za-z&.\-]+", t) if len(w) > 1]
    common = set("download latest report reports annual quarterly from the of to and get all files filings documents".split())
    cand = [w for w in tokens if w.lower() not in common]
    company = cand[0] if cand else "Unknown"

    years = _extract_years(t)
    extras = _detect_periods(t)
    return Intent(company=company, doc_type=doc_type, doc_types=doc_types, years=years, extras=extras)
