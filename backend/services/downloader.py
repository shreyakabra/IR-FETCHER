import os, hashlib, mimetypes
import logging
from ..models import FoundFile, DownloadedFile
from ..agents.naming import build_path
from ..util.http import get_bytes
from ..util.text import safe_name
from ..config import DOWNLOAD_ROOT
from typing import Optional

logger = logging.getLogger(__name__)

def _ext_from_mime(mt: Optional[str]) -> str:
    if not mt:
        return ".bin"
    guess = mimetypes.guess_extension(mt.split(";")[0].strip())
    return guess or ".bin"

async def download_one(company: str, doc_type: str, year: Optional[int], f: FoundFile) -> Optional[DownloadedFile]:
    try:
        logger.info(f"Downloading {f.url} for {company} {doc_type} {year}")
        data, mime = await get_bytes(f.url)
        sha256 = hashlib.sha256(data).hexdigest()
        ext = _ext_from_mime(mime)
        folder, filename = build_path(company, doc_type, year, ext)
        out_dir = os.path.join(DOWNLOAD_ROOT, safe_name(company), safe_name(doc_type), str(year) if year else "unknown")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)
        with open(out_path, "wb") as w:
            w.write(data)
        logger.info(f"Successfully downloaded to {out_path}")
        return DownloadedFile(
            company=company, doc_type=doc_type, year=year,
            file_path=out_path, filename=filename, url=f.url,
            sha256=sha256, mimetype=mime or "", source=f.source
        )
    except Exception as e:
        logger.error(f"Failed to download {f.url}: {str(e)}", exc_info=True)
        return None
