"""
Database storage backend for IR-FETCHER.

Supports SQLite (local development) and Supabase (managed Postgres) deployments.
"""
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

try:
    from supabase import Client, create_client
except Exception:  # pragma: no cover - optional dependency
    Client = None
    create_client = None

logger = logging.getLogger(__name__)

DATABASE_BACKEND = os.getenv("DATABASE_BACKEND", "sqlite").strip().lower()
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", DATA_DIR / "database.db"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "files")

_sqlite_conn: Optional[sqlite3.Connection] = None
_sqlite_lock = Lock()
_supabase_client: Optional["Client"] = None

DB_FIELDS = [
    "company",
    "doc_type",
    "year",
    "file_path",
    "filename",
    "url",
    "sha256",
    "mimetype",
    "source",
    "indexed_at",
    "created_at",
]


def _ensure_backend():
    if DATABASE_BACKEND not in {"sqlite", "supabase"}:
        raise ValueError(
            f"Unsupported DATABASE_BACKEND '{DATABASE_BACKEND}'. "
            "Use 'sqlite' or 'supabase'."
        )


def _get_sqlite_conn() -> sqlite3.Connection:
    global _sqlite_conn
    if _sqlite_conn is None:
        os.makedirs(SQLITE_PATH.parent, exist_ok=True)
        _sqlite_conn = sqlite3.connect(str(SQLITE_PATH), check_same_thread=False)
        _sqlite_conn.row_factory = sqlite3.Row
    return _sqlite_conn


def _get_supabase_client() -> "Client":
    global _supabase_client
    if create_client is None:
        raise ImportError(
            "supabase client is not installed. Add 'supabase' to requirements."
        )
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Supabase credentials are missing. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)."
        )
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def _normalize_metadata(file_data: Dict) -> Dict:
    indexed_at = file_data.get("indexed_at")
    if not indexed_at:
        indexed_at = int(datetime.utcnow().timestamp())
    doc = {
        "company": file_data["company"],
        "doc_type": file_data["doc_type"],
        "year": file_data.get("year"),
        "file_path": file_data["file_path"],
        "filename": file_data["filename"],
        "url": file_data["url"],
        "sha256": file_data["sha256"],
        "mimetype": file_data.get("mimetype"),
        "source": file_data.get("source"),
        "indexed_at": indexed_at,
        "created_at": file_data.get("created_at")
        or datetime.utcnow().isoformat(timespec="seconds"),
    }
    return doc


def init_database():
    _ensure_backend()
    if DATABASE_BACKEND == "sqlite":
        conn = _get_sqlite_conn()
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    year INTEGER,
                    file_path TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    url TEXT NOT NULL,
                    sha256 TEXT NOT NULL UNIQUE,
                    mimetype TEXT,
                    source TEXT,
                    indexed_at INTEGER,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_company ON files(company);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_doc_type ON files(doc_type);"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_year ON files(year);")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_indexed_at ON files(indexed_at DESC);"
            )
        logger.info("SQLite database ready at %s", SQLITE_PATH)
    else:
        _get_supabase_client()
        logger.info(
            "Supabase backend configured (table='%s', url='%s')",
            SUPABASE_TABLE,
            SUPABASE_URL,
        )


def save_file_metadata(file_data: Dict) -> bool:
    doc = _normalize_metadata(file_data)
    try:
        if DATABASE_BACKEND == "sqlite":
            conn = _get_sqlite_conn()
            with _sqlite_lock, conn:
                cursor = conn.execute(
                    """
                    INSERT INTO files (
                        company, doc_type, year, file_path, filename,
                        url, sha256, mimetype, source, indexed_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(sha256) DO NOTHING;
                    """,
                    tuple(doc[field] for field in DB_FIELDS),
                )
                inserted = cursor.rowcount and cursor.rowcount > 0
                if not inserted:
                    logger.info(
                        "File with sha256 %s already exists, skipping",
                        doc["sha256"][:8],
                    )
                return inserted
        else:
            client = _get_supabase_client()
            response = (
                client.table(SUPABASE_TABLE)
                .insert(doc)
                .execute()
            )
            if getattr(response, "error", None):
                raise RuntimeError(response.error)
            return bool(response.data)
    except Exception as exc:
        logger.error("Error saving file metadata: %s", exc, exc_info=True)
        return False


def get_recent_files(limit: int = 100) -> List[Dict]:
    try:
        if DATABASE_BACKEND == "sqlite":
            conn = _get_sqlite_conn()
            cursor = conn.execute(
                """
                SELECT company, doc_type, year, file_path, filename,
                       url, sha256, mimetype, source, indexed_at, created_at
                FROM files
                ORDER BY indexed_at DESC
                LIMIT ?;
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
        client = _get_supabase_client()
        response = (
            client.table(SUPABASE_TABLE)
            .select("*")
            .order("indexed_at", desc=True)
            .limit(limit)
            .execute()
        )
        if getattr(response, "error", None):
            raise RuntimeError(response.error)
        return response.data or []
    except Exception as exc:
        logger.error("Error fetching recent files: %s", exc, exc_info=True)
        return []


def search_files(
    company: Optional[str] = None,
    doc_type: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 100,
) -> List[Dict]:
    filters: Dict = {}
    if company:
        filters["company"] = company
    if doc_type:
        filters["doc_type"] = doc_type
    if year:
        filters["year"] = year

    try:
        if DATABASE_BACKEND == "sqlite":
            conn = _get_sqlite_conn()
            where_clauses = []
            params: List[object] = []
            for key, value in filters.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)
            sql_where = ""
            if where_clauses:
                sql_where = "WHERE " + " AND ".join(where_clauses)
            params.append(limit)
            cursor = conn.execute(
                f"""
                SELECT company, doc_type, year, file_path, filename,
                       url, sha256, mimetype, source, indexed_at, created_at
                FROM files
                {sql_where}
                ORDER BY indexed_at DESC
                LIMIT ?;
                """,
                tuple(params),
            )
            return [dict(row) for row in cursor.fetchall()]

        client = _get_supabase_client()
        query = client.table(SUPABASE_TABLE).select("*")
        for key, value in filters.items():
            query = query.eq(key, value)
        response = (
            query.order("indexed_at", desc=True)
            .limit(limit)
            .execute()
        )
        if getattr(response, "error", None):
            raise RuntimeError(response.error)
        return response.data or []
    except Exception as exc:
        logger.error("Error searching files: %s", exc, exc_info=True)
        return []

