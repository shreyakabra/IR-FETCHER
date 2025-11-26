from ..util.text import safe_name
from typing import Optional

def build_path(company: str, doc_type: str, year: Optional[int], ext: str):
    folder = safe_name(company, doc_type, str(year) if year else "")
    filename = safe_name(company, doc_type, str(year) if year else "") + ext
    return folder, filename
