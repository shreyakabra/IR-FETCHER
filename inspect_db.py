import sqlite3
from pathlib import Path
path = Path('data/database.db')
print('exists', path.exists(), 'size', path.stat().st_size if path.exists() else None)
if path.exists():
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='files'")
    print('table exists', cur.fetchone())
    cur.execute("SELECT count(*) FROM files")
    print('rows', cur.fetchone())
    for row in cur.execute("SELECT company, doc_type, year FROM files LIMIT 5"):
        print(row)
    conn.close()
