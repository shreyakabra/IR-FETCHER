from typing import List
from ..models import Intent, FoundFile
import requests
from bs4 import BeautifulSoup
import logging
from ..util.text import guess_year_from_title
from tavily import TavilyClient
import os

logger = logging.getLogger(__name__)

def candidate_ir_urls(company: str):
    # quick heuristics; expand with public company → domain mapping later
    base = company.replace(" ", "").lower()
    return [
        f"https://{base}.com/investors",
        f"https://{base}.com/investor-relations",
        f"https://investor.{base}.com",
        f"https://ir.{base}.com",
        f"https://{base}.in/investors",
        f"https://www.{base}.com/investors",
    ]

def find_ir_pages_with_tavily(company: str) -> List[str]:
    """Use Tavily to find actual IR page URLs"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    
    try:
        tv = TavilyClient(api_key=api_key)
        query = f'"{company}" investor relations site'
        res = tv.search(query, max_results=5)
        
        ir_urls = []
        for item in res.get("results", []):
            url = item.get("url", "")
            if url and any(term in url.lower() for term in ['investor', 'ir.', 'investor-relations']):
                ir_urls.append(url)
        
        return ir_urls[:5]
    except Exception as e:
        logger.error(f"Error finding IR pages with Tavily: {e}")
        return []

def find_ir_documents(intent: Intent) -> List[FoundFile]:
    titles = ["annual report", "10-k", "20-f", "investor presentation", "results", "financials", "quarterly", "earnings"]
    found = []
    
    # First, try to find IR pages using Tavily
    tavily_ir_urls = find_ir_pages_with_tavily(intent.company)
    all_ir_urls = list(set(tavily_ir_urls + candidate_ir_urls(intent.company)))
    
    logger.info(f"Checking {len(all_ir_urls)} IR URLs for {intent.company}")
    
    for u in all_ir_urls:
        try:
            html = requests.get(u, timeout=15, headers={"User-Agent": "Mozilla/5.0"}).text
            soup = BeautifulSoup(html, "lxml")
            
            # Look for PDF links
            for a in soup.find_all("a", href=True):
                href = a["href"]
                txt = (a.get_text() or "").lower()
                
                # Check if it's a PDF or document link
                is_pdf_link = href.lower().endswith('.pdf') or 'pdf' in href.lower()
                matches_title = any(t in txt for t in titles) or any(t in href.lower() for t in titles)
                
                if is_pdf_link or matches_title:
                    if href.startswith("/"):
                        href = u.rstrip("/") + href
                    elif not href.startswith("http"):
                        continue
                    
                    year = guess_year_from_title(txt) or guess_year_from_title(href) or (intent.years[0] if intent.years else None)
                    
                    found.append(FoundFile(
                        url=href, 
                        title=a.get_text().strip() or href, 
                        year=year,
                        mimetype="application/pdf" if is_pdf_link else None,
                        source="IR", 
                        confidence=0.7 if is_pdf_link else 0.6
                    ))
        except Exception as e:
            logger.debug(f"Error scraping {u}: {e}")
            continue
    
    logger.info(f"IR scraper found {len(found)} documents")
    return found[:30]
