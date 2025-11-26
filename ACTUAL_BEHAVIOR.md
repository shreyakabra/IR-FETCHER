# Actual Behavior vs Intended Behavior

## Issues Identified

### 1. **Parser is Too Basic (Not LLM-Based)**
**Problem**: The `parse_prompt()` function in `backend/agents/parser.py` uses simple regex and heuristics, NOT an LLM as described.

**Current Implementation**:
- Extracts company name by taking the first capitalized word that's not a common word
- This fails for prompts like:
  - "Get Apple's annual report" → might extract "Get" or wrong word
  - "Download Tesla 10-K" → might work, but unreliable
  - Multi-word company names like "Johnson & Johnson" → will fail

**What Should Happen**: Use OpenAI API to parse the prompt intelligently (the code references `OPENAI_API_KEY` but doesn't use it for parsing).

### 2. **Tavily API Dependency**
**Problem**: Both `web_search.py` and `ir_scraper.py` require `TAVILY_API_KEY`. If not set:
- `web_find_documents()` returns empty list immediately
- `find_ir_pages_with_tavily()` returns empty list
- Only basic URL guessing remains for IR scraping

**Current Behavior**: 
- If `TAVILY_API_KEY` is missing → web search returns nothing
- Falls back to SEC and IR scraping, but those are also limited

### 3. **SEC Scraper is Very Naive**
**Problem**: `find_sec_documents()` in `backend/services/sec.py`:
- Just searches HTML text for "10-K" or "Annual report" strings
- Doesn't properly parse SEC EDGAR structure
- Doesn't follow links to actual PDF documents
- Returns HTML page URLs, not PDF URLs

**Current Behavior**: Returns mostly HTML pages, not downloadable PDFs.

### 4. **IR Scraper Limitations**
**Problem**: `find_ir_documents()`:
- Relies on Tavily to find IR pages (fails if no API key)
- Falls back to URL guessing (e.g., `tesla.com/investors`)
- Many companies don't follow these URL patterns
- Scrapes HTML but might miss PDFs behind JavaScript or dynamic content

### 5. **No Error Handling for Missing Dependencies**
**Problem**: The app silently fails when:
- `TAVILY_API_KEY` is missing → returns empty results
- API calls fail → returns empty results
- Downloads fail → just logs warning, continues

**User Experience**: User gets empty results with no clear error message about why.

## What Actually Works

✅ **Basic Structure**: The pipeline architecture is correct
✅ **File Organization**: Downloads are organized by company/doc_type/year
✅ **Metadata Storage**: SHA256 hashes and metadata are saved correctly
✅ **API Endpoints**: FastAPI endpoints are properly set up
✅ **Year Extraction**: Regex-based year extraction works for simple cases

## What Doesn't Work as Described

❌ **Intelligent Prompt Parsing**: Not using LLM, just regex
❌ **Multi-Source Search**: Depends heavily on Tavily API
❌ **SEC Integration**: Very basic, doesn't get actual PDFs
❌ **Robust Company Name Extraction**: Fails for many company names
❌ **Error Reporting**: Silent failures, no user feedback

## Recommendations

1. **Implement LLM-based parsing** using OpenAI API (already in requirements)
2. **Add fallback search strategies** that don't require Tavily
3. **Improve SEC scraper** to use SEC API properly or better HTML parsing
4. **Add better error messages** when API keys are missing
5. **Improve company name extraction** with LLM or better heuristics
6. **Add validation** to check API keys before starting search

