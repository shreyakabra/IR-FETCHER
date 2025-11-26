from typing import List
from ..models import Intent, FoundFile
from ..util.text import guess_year_from_title
import requests

# Simple EDGAR "company facts" + "full-text search" is large; MVP uses SEC's "company-search" + filter.
# For production, use SEC API w/ proper User-Agent and rate limits.

UA = {"User-Agent": "IR-Downloader/1.0 contact@example.com"}

def find_sec_documents(intent: Intent) -> List[FoundFile]:
    # heuristic: search sec for company then look for 10-K or annual report filings via "full-text search" page.
    q = intent.company
    try:
        search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={q}&owner=exclude&action=getcompany"
        r = requests.get(search_url, headers=UA, timeout=30)
        if r.status_code != 200:
            return []
        # naive scrape for 10-K document links (MVP); improve with edgar API later
        hits = []
        for m in r.text.splitlines():
            if ("10-K" in m or "Annual report" in m) and ".htm" in m:
                # this is intentionally rough; you'd switch to BeautifulSoup + follow document pages to get .pdf
                # add minimal record; downloader will resolve Content-Type later
                try:
                    if '"' in m:
                        url_parts = m.split('"')
                        if len(url_parts) > 1:
                            url = "https://www.sec.gov" + url_parts[1]
                        else:
                            url = search_url
                    else:
                        url = search_url
                    year = guess_year_from_title(m)
                    hits.append(FoundFile(url=url, title=m.strip(), year=year, mimetype=None, source="SEC", confidence=0.7))
                except Exception:
                    continue
        return hits[:30]
    except Exception:
        return []
