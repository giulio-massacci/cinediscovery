# 🎬 CineDiscovery

> **Never miss a great film on TV — and always know where else you can watch it.**

CineDiscovery scrapes the Italian weekly TV schedule, cross-references every film against the TMDB database, and tells you instantly whether it's also available on streaming platforms, available to buy, or rent. All in a clean, filterable Streamlit dashboard.

---

## ✨ Features

- 📺 **Full weekly TV schedule** — fetches films airing across all major Italian channels for the entire week
- 🔍 **TMDB enrichment** — for each film, retrieves streaming, purchase, and rental availability (Italian market)
- ⚡ **Smart caching** — results are stored locally in a SQLite database so repeated runs are instant
- 🎛️ **Live filters** — filter by title, channel, date, or availability status in real time
- 🗓️ **Chronological ordering** — films are sorted correctly even across month boundaries
- 🔄 **Resilient fetching** — automatic retry with exponential backoff on network errors

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A free [TMDB API key](https://www.themoviedb.org/settings/api)

### Installation

```bash
git clone https://github.com/giulio-massacci/cinediscovery.git
cd cinediscovery
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_api_key_here
```

### Run

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🗂️ Project Structure

```
cinediscovery/
├── app.py              # Streamlit UI
├── config.py           # Configuration & constants
├── db.py               # SQLite cache layer
├── requirements.txt
└── sources/
    ├── tmdb.py         # TMDB API client
    ├── tvprograms.py   # TV schedule scraper
    └── utils.py        # Shared utilities
```

---

## 🎨 Availability Legend

| Badge | Meaning |
|-------|---------|
| 🟢 Only on TV | Not available on any platform — catch it live! |
| 🟠 Available on platforms | Streamable on at least one service |
| 🔵 Pay only | Available to buy or rent, but not on subscription streaming |
| ⚪ Not found on TMDB | Film not matched in the TMDB database |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| [Streamlit](https://streamlit.io) | Interactive web dashboard |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | TV schedule scraping |
| [TMDB API](https://www.themoviedb.org/documentation/api) | Film metadata & watch providers |
| [pandas](https://pandas.pydata.org) | Data wrangling |
| SQLite | Local result caching |

---

## ⚠️ Disclaimer

This product uses the TMDB API but is not endorsed or certified by TMDB.
TV schedule data is scraped from publicly available sources for personal use only.

---

<p align="center">Made with ❤️ and too many late-night movies.</p>
