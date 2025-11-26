from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class DownloadRequest(BaseModel):
    prompt: str = Field(..., description="Natural language ask")
    max_items: Optional[int] = None
    prefer_official: bool = True
    company_hint: Optional[str] = None
    ticker: Optional[str] = None
    year_window: Optional[int] = None

class Intent(BaseModel):
    company: str
    doc_type: str        # e.g., "annual report", "10-K", "press video"
    years: List[int]     # e.g., [2020, 2021, 2022, 2023, 2024]
    region: Optional[str] = None
    doc_types: List[str] = Field(default_factory=list)
    extras: Dict[str, str] = Field(default_factory=dict)

class FoundFile(BaseModel):
    url: str
    title: str
    year: Optional[int]
    mimetype: Optional[str]
    source: str          # "SEC", "IR", "Web"
    confidence: float

class DownloadedFile(BaseModel):
    company: str
    doc_type: str
    year: Optional[int]
    file_path: str
    filename: str
    url: str
    sha256: str
    mimetype: str
    source: str

class DownloadResponse(BaseModel):
    intent: Intent
    results: List[DownloadedFile]

class ApiSettings(BaseModel):
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None
    default_provider: Optional[str] = None
