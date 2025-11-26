from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .models import DownloadRequest, DownloadResponse, ApiSettings
from .pipeline import run_pipeline
from .settings import load_settings_status, update_settings_env, SETTING_KEYS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = FastAPI(title="IR Downloader", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "IR Downloader API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "download": "/download (POST)",
            "files": "/files",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/download", response_model=DownloadResponse)
async def download(req: DownloadRequest):
    return await run_pipeline(req)

# handy: list recent files
from .database import get_recent_files, init_database

# Initialize database on startup
init_database()

@app.get("/files")
def files():
    """Get recent files from database."""
    items = get_recent_files(limit=100)
    return {"items": items}

@app.get("/settings")
def get_settings():
    return load_settings_status()

@app.post("/settings")
def update_settings(body: ApiSettings):
    incoming = body.model_dump(exclude_none=True)
    if not incoming:
        return {"updated": []}
    update_settings_env(incoming)
    return {"updated": list(incoming.keys())}
