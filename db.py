import sqlite3
import json
import config

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init() -> None:
    """Create the cache table if it doesn't exist yet."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tmdb_cache (
                title       TEXT PRIMARY KEY COLLATE NOCASE,
                not_found   INTEGER NOT NULL DEFAULT 0,
                streaming   TEXT,
                purchase    TEXT,
                rent        TEXT,
                cached_at   TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)


def purge_old(years: int = 1) -> int:
    """Delete cached entries older than `years` years. Returns the number of deleted rows."""
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM tmdb_cache WHERE cached_at < datetime('now', ?)",
            (f"-{years} year",),
        )
        return cur.rowcount


def get_all() -> dict:
    """Return {title.lower(): (streaming, purchase, rent)} for every cached entry.

    - Title absent from the dict → not yet fetched.
    - Value (None, None, None) → movie not found on TMDB.
    - Value (list, list, list) → movie found; lists may be empty.
    """
    with _connect() as conn:
        rows = conn.execute(
            "SELECT title, not_found, streaming, purchase, rent FROM tmdb_cache"
        ).fetchall()

    result: dict = {}
    for row in rows:
        if row["not_found"]:
            result[row["title"].lower()] = (None, None, None)
        else:
            result[row["title"].lower()] = (
                json.loads(row["streaming"]) if row["streaming"] else [],
                json.loads(row["purchase"]) if row["purchase"] else [],
                json.loads(row["rent"]) if row["rent"] else [],
            )
    return result


def save(title: str, streaming, purchase, rent) -> None:
    """Upsert a TMDB result.  Pass (None, None, None) for titles not found."""
    not_found = int(streaming is None and purchase is None and rent is None)
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO tmdb_cache (title, not_found, streaming, purchase, rent)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(title) DO UPDATE SET
                not_found = excluded.not_found,
                streaming = excluded.streaming,
                purchase  = excluded.purchase,
                rent      = excluded.rent,
                cached_at = datetime('now')
            """,
            (
                title,
                not_found,
                json.dumps(streaming) if streaming is not None else None,
                json.dumps(purchase)  if purchase  is not None else None,
                json.dumps(rent)      if rent      is not None else None,
            ),
        )
