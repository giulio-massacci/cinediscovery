"""Standalone scraper: fetches TV schedule + TMDB providers and writes data/films.json.

Run manually or via GitHub Actions (see .github/workflows/scrape.yml).
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from sources.tmdb import TMDB
from sources.tvprograms import TVProgramms

OUTPUT = Path(__file__).parent / "data" / "films.json"
TMDB_DELAY = 0.25  # seconds between TMDB calls to avoid rate limiting


def _availability(streaming, purchase, rent, not_found):
    if not_found:
        return "⚪Not found on TMDB"
    if not streaming and not purchase and not rent:
        return "🟢Only on TV"
    if streaming:
        return "🟠Available on platforms"
    return "🔵Pay only"


def main():
    OUTPUT.parent.mkdir(exist_ok=True)

    print("Fetching TV schedule...")
    films_raw = TVProgramms().get_all_films()
    # each entry: [day, number, time, title, channel]
    print(f"  Found {len(films_raw)} films.")

    tmdb = TMDB()
    results = []

    for idx, (day, number, time_str, title, channel) in enumerate(films_raw, 1):
        print(f"  [{idx}/{len(films_raw)}] {title}")
        streaming, purchase, rent, rating, director, tmdb_url = tmdb.get_film_data(title)
        not_found = streaming is None
        results.append({
            "day": day,
            "number": number,
            "date": f"{day} {number}",
            "time": time_str,
            "title": title,
            "channel": channel,
            "not_found": not_found,
            "streaming": streaming or [],
            "purchase": purchase or [],
            "rent": rent or [],
            "availability": _availability(streaming, purchase, rent, not_found),
            "rating": rating,
            "director": director,
            "tmdb_url": tmdb_url or "",
        })
        time.sleep(TMDB_DELAY)

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "films": results,
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(results)} films → {OUTPUT}")


if __name__ == "__main__":
    main()
