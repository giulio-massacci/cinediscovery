import requests
import config


class TMDB:

    def __init__(self):
        self.api_key = config.TMDB_API_KEY

    def _search_movie_id(self, title):
        r = requests.get(
            f"{config.TMDB_BASE}/search/movie",
            params={"api_key": self.api_key, "query": title, "language": "it-IT"},
            timeout=10
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        return results[0]["id"] if results else None

    def get_providers(self, title, country="IT"):
        movie_id = self._search_movie_id(title)
        if movie_id is None:
            return None, None, None
        r = requests.get(
            f"{config.TMDB_BASE}/movie/{movie_id}/watch/providers",
            params={"api_key": self.api_key},
            timeout=10
        )
        r.raise_for_status()
        data = r.json().get("results", {}).get(country, {})
        streaming = [p["provider_name"] for p in data.get("flatrate", [])]
        acquisto = [p["provider_name"] for p in data.get("buy", [])]
        noleggio = [p["provider_name"] for p in data.get("rent", [])]
        return streaming, acquisto, noleggio
