import os
from dotenv import load_dotenv
load_dotenv()

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

URL_PROGRAMS = "https://www.programmitv.com/film-"
URL_DAYS = [
    "lunedi",
    "martedi",
    "mercoledi",
    "giovedi",
    "venerdi",
    "sabato",
    "domenica"
]

ITA_W_DAYS = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]