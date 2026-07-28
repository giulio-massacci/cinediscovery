# 🎬 CineDiscovery

> **A weekly guide to films on Italian TV, with streaming availability at a glance.**

CineDiscovery scrapes the Italian weekly TV schedule and cross-references every film against the TMDB database — giving you rating, director, streaming availability, and a direct link to the TMDB page. All in a clean, filterable Streamlit dashboard.

---

## ✨ Features

- 📺 **Full weekly TV schedule** — films airing across all major Italian channels for the entire week
- 🔍 **TMDB enrichment** — streaming, purchase, and rental availability for the Italian market; plus rating, director, and link to the TMDB page
- 🏆 **Top films cards** — visual card grid highlighting the 15 highest-rated films of the week, color-coded by availability and clickable to open TMDB
- 📊 **Top 20 rating chart** — horizontal bar chart of the top 20 films by TMDB rating
- 🎛️ **Live filters** — filter by title, channel, date, or availability status
- 🗓️ **Chronological ordering** — films sorted correctly even across month boundaries
- 🔄 **Resilient fetching** — automatic retry with exponential backoff on network errors
- ⚙️ **GitHub Actions automation** — daily scrape runs as a scheduled workflow, commits `data/films.json` to the repo; the Streamlit app only reads static data

---

## 🏗️ Architecture

Data collection and the Streamlit UI are fully decoupled:

```
GitHub Actions (daily @ 05:00 UTC)
  └── scrape.py  →  data/films.json  →  committed to repo
                                              │
                                    Streamlit Cloud reads it
                                    on every page load
```

This means the Streamlit app has **zero network calls at runtime** — it just reads a pre-built JSON file.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A free [TMDB API key](https://www.themoviedb.org/settings/api)

### Installation

```bash
git clone https://github.com/your-username/cinediscovery.git
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

### Populate data locally

```bash
python scrape.py
```

### Run the app

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deploying to Streamlit Cloud

1. Push the repo to GitHub
2. Add `TMDB_API_KEY` as a **repository secret** (Settings → Secrets → Actions)
3. Deploy `app.py` on [Streamlit Cloud](https://streamlit.io/cloud)
4. The GitHub Action runs daily and commits updated data — Streamlit Cloud reboots automatically on each new commit

---

## 🗂️ Project Structure

```
cinediscovery/
├── app.py              # Streamlit UI (read-only, no API calls)
├── scrape.py           # Standalone scraper (run by GitHub Actions)
├── config.py           # Configuration & constants
├── requirements.txt
├── data/
│   └── films.json      # Generated daily by scrape.py
├── .github/
│   └── workflows/
│       └── scrape.yml  # Scheduled GitHub Action
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
| 🟠 Available on platforms | Streamable on at least one subscription service |
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
