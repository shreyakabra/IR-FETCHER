from typing import List
import asyncio
import logging
from ..models import Intent, FoundFile
from ..services.sec import find_sec_documents
from ..services.ir_scraper import find_ir_documents
from ..services.web_search import web_find_documents

logger = logging.getLogger(__name__)

async def route_search(intent: Intent) -> List[FoundFile]:
    # Run blocking search functions in thread pool to avoid blocking async event loop
    loop = asyncio.get_event_loop()
    all_results = []
    
    # Strategy 1: Use Tavily as primary search (most reliable for PDFs)
    tavily_hits = await loop.run_in_executor(None, web_find_documents, intent)
    if tavily_hits:
        logger.info(f"Tavily found {len(tavily_hits)} documents")
        all_results.extend(tavily_hits)
    
    # Strategy 2: Try SEC for U.S. public companies + 10-K/annual (if Tavily didn't find enough)
    if len(all_results) < 5 and intent.doc_type in {"10-K", "annual report"}:
        sec_hits = await loop.run_in_executor(None, find_sec_documents, intent)
        if sec_hits:
            logger.info(f"SEC found {len(sec_hits)} documents")
            all_results.extend(sec_hits)
    
    # Strategy 3: Try IR site scraping (if still not enough)
    if len(all_results) < 5:
        ir_hits = await loop.run_in_executor(None, find_ir_documents, intent)
        if ir_hits:
            logger.info(f"IR scraper found {len(ir_hits)} documents")
            all_results.extend(ir_hits)
    
    # Remove duplicates by URL and sort by confidence
    seen = set()
    unique_results = []
    for result in all_results:
        if result.url not in seen:
            seen.add(result.url)
            unique_results.append(result)
    
    # Sort by confidence
    unique_results.sort(key=lambda x: x.confidence, reverse=True)
    
    logger.info(f"Total unique documents found: {len(unique_results)}")
    return unique_results