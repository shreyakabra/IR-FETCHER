import os, json, time
from ..models import DownloadedFile
from ..config import METADATA_ROOT
from ..util.text import safe_name
from ..database import save_file_metadata, init_database

# Initialize database on import
init_database()

def write_metadata(df: DownloadedFile):
    """Write metadata to both database and JSON file (for backward compatibility)."""
    metadata_dict = {
        "company": df.company,
        "doc_type": df.doc_type,
        "year": df.year,
        "file_path": df.file_path,
        "filename": df.filename,
        "url": df.url,
        "sha256": df.sha256,
        "mimetype": df.mimetype,
        "source": df.source,
        "indexed_at": int(time.time())
    }
    
    # Save to database (primary storage)
    save_file_metadata(metadata_dict)
    
    # Also save to JSON file for backward compatibility
    os.makedirs(METADATA_ROOT, exist_ok=True)
    name = safe_name(df.company, df.doc_type, str(df.year) if df.year else "unknown", df.sha256[:8]) + ".json"
    path = os.path.join(METADATA_ROOT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata_dict, f, indent=2)
    return path
