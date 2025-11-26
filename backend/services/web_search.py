from typing import List
from ..models import Intent, FoundFile
from tavily import TavilyClient
import os
import logging
from ..util.text import guess_year_from_title

logger = logging.getLogger(__name__)

def web_find_documents(intent: Intent) -> List[FoundFile]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY not found in environment variables")
        return []
    
    try:
        tv = TavilyClient(api_key=api_key)
        
        # Build better search query for PDFs
        company = intent.company
        doc_type = intent.doc_type
        
        period_terms = []
        extras = intent.extras or {}
        if extras.get("quarter"):
            quarter = extras["quarter"]
            period_terms = {
                "Q1": ['"Q1"', '"first quarter"'],
                "Q2": ['"Q2"', '"second quarter"'],
                "Q3": ['"Q3"', '"third quarter"'],
                "Q4": ['"Q4"', '"fourth quarter"'],
            }.get(quarter, [f'"{quarter}"'])
        elif extras.get("half"):
            half = extras["half"]
            period_terms = {
                "H1": ['"H1"', '"first half"', '"semi annual"'],
                "H2": ['"H2"', '"second half"'],
            }.get(half, [f'"{half}"'])

        period_str = ""
        if period_terms:
            period_str = " " + " ".join(period_terms)

        # If multiple years specified (year window), search more broadly
        # Otherwise use specific year
        if intent.years and len(intent.years) > 1:
            # Year window: search without specific year to get broader results
            year_str = ""
            # Also add queries for each year in the window
            year_queries = []
            for year in intent.years[:3]:  # Limit to first 3 years to avoid too many queries
                year_queries.extend([
                    f'"{company}" "{doc_type}"{period_str} {year} filetype:pdf',
                    f'"{company}" investor relations "{doc_type}"{period_str} {year} PDF',
                ])
        else:
            year_str = f" {intent.years[0]}" if intent.years else ""
            year_queries = []
        
        # Multiple search strategies
        queries = [
            # Direct PDF search
            f'"{company}" "{doc_type}"{period_str}{year_str} filetype:pdf',
            # IR site search
            f'"{company}" investor relations "{doc_type}"{period_str}{year_str} PDF',
            # Company website search
            f'site:{company.lower().replace(" ", "")}.com "{doc_type}"{period_str}{year_str} PDF',
            # Generic search
            f'{company} {doc_type}{period_str}{year_str} PDF download',
        ]
        
        # Add year-specific queries if year window is used
        queries.extend(year_queries)
        
        all_results = []
        seen_urls = set()
        
        for query in queries:
            try:
                logger.info(f"Tavily search query: {query}")
                # Increase max_results when searching for year window to get more results
                max_res = 20 if intent.years and len(intent.years) > 1 else 10
                res = tv.search(query, max_results=max_res, search_depth="advanced")
                
                for item in res.get("results", []):
                    url = item.get("url", "")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Prefer PDF URLs
                    is_pdf = url.lower().endswith('.pdf') or 'pdf' in url.lower()
                    title = item.get("title") or item.get("url", "")
                    year = guess_year_from_title(title) or (intent.years[0] if intent.years else None)
                    
                    # Extract year from content if available
                    content = item.get("content", "")
                    if not year and content:
                        year = guess_year_from_title(content)
                    
                    confidence = item.get("score", 0.5)
                    if is_pdf:
                        confidence += 0.2  # Boost PDFs
                    
                    all_results.append(FoundFile(
                        url=url,
                        title=title,
                        year=year,
                        mimetype="application/pdf" if is_pdf else None,
                        source="Tavily",
                        confidence=min(confidence, 1.0)
                    ))
            except Exception as e:
                logger.error(f"Tavily search error for query '{query}': {e}")
                continue
        
        # Sort by confidence and return top results
        all_results.sort(key=lambda x: x.confidence, reverse=True)
        logger.info(f"Tavily found {len(all_results)} documents")
        # Return more results when year window is used to ensure we have enough for all years
        max_return = 50 if intent.years and len(intent.years) > 1 else 20
        return all_results[:max_return]
        
    except Exception as e:
        logger.error(f"Tavily client error: {e}", exc_info=True)
        return []
