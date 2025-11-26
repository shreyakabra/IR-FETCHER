import re
from slugify import slugify

def guess_year_from_title(t: str):
    if not t:
        return None

    # Handle fiscal-year style ranges like "2024-25" or "2023-2024"
    range_match = re.search(r"(20\d{2})\s*[-/–—]\s*(\d{2,4})", t)
    if range_match:
        start_year = int(range_match.group(1))
        end_raw = range_match.group(2)
        if len(end_raw) == 2:
            end_year = int(str(start_year)[:2] + end_raw)
        else:
            end_year = int(end_raw)
        if end_year >= start_year - 1:
            return end_year

    fy_match = re.search(r"fy[\s\-]?(\d{2,4})", t, flags=re.IGNORECASE)
    if fy_match:
        raw = fy_match.group(1)
        if len(raw) == 2:
            val = int(raw)
            return 2000 + val
        return int(raw)

    years = re.findall(r"(20\d{2})", t)
    if years:
        return int(max(years))
    return None

def safe_name(*parts):
    joined = "_".join([p for p in parts if p])
    return slugify(joined, separator="_")
