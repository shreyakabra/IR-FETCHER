"""
Quick smoke test for the database layer.

Run with:
    python test_database.py

It forces the backend into SQLite mode, writes a test record, and prints the
results of both search and recent queries.
"""
import importlib
import os
import tempfile
import time
from pathlib import Path

os.environ["DATABASE_BACKEND"] = "sqlite"
tmp_db = Path(tempfile.gettempdir()) / "ir_fetcher_test.db"
os.environ["SQLITE_PATH"] = str(tmp_db)

import backend.database as database  # noqa: E402

importlib.reload(database)


def main():
    database.init_database()
    payload = {
        "company": "Example Co",
        "doc_type": "annual_report",
        "year": 2024,
        "file_path": "data/downloads/example.pdf",
        "filename": "example.pdf",
        "url": "https://example.com/example.pdf",
        "sha256": str(time.time()),
        "mimetype": "application/pdf",
        "source": "smoke-test",
    }
    database.save_file_metadata(payload)

    print("Recent files:", database.get_recent_files(limit=3))
    print("Search Example Co:", database.search_files(company="Example Co", limit=3))


if __name__ == "__main__":
    main()

