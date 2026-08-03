import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DB_PATH = Path(__file__).parent / "cache.db"

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

URL_PROGRAMS = "https://programmitv.com/film-"
URL_DAYS = [
    "stasera",
    "lunedi",
    "martedi",
    "mercoledi",
    "giovedi",
    "venerdi",
    "sabato",
    "domenica"
]

ITA_W_DAYS = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

MONTHS = {
    "gennaio":1,"febbraio":2,"marzo":3,"aprile":4,"maggio":5,"giugno":6,
    "luglio":7,"agosto":8,"settembre":9,"ottobre":10,"novembre":11,"dicembre":12
}