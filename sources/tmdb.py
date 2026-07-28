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

    def get_film_data(self, title, country="IT"):
        """Return (streaming, purchase, rent, rating, director, tmdb_url).

        All values are None when the movie is not found on TMDB.
        Uses append_to_response to fetch details + credits + providers in one call.
        """
        movie_id = self._search_movie_id(title)
        if movie_id is None:
            return None, None, None, None, None, None

        r = requests.get(
            f"{config.TMDB_BASE}/movie/{movie_id}",
            params={
                "api_key": self.api_key,
                "append_to_response": "credits,watch/providers",
                "language": "it-IT",
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        # Watch providers
        providers = data.get("watch/providers", {}).get("results", {}).get(country, {})
        streaming = [p["provider_name"] for p in providers.get("flatrate", [])]
        purchase  = [p["provider_name"] for p in providers.get("buy", [])]
        rent      = [p["provider_name"] for p in providers.get("rent", [])]

        # Rating (global vote average, rounded to 1 decimal)
        vote = data.get("vote_average")
        rating = round(vote, 1) if vote else None

        # Director(s)
        crew = data.get("credits", {}).get("crew", [])
        directors = [m["name"] for m in crew if m.get("job") == "Director"]
        director = ", ".join(directors) if directors else None

        tmdb_url = f"https://www.themoviedb.org/movie/{movie_id}"

        return streaming, purchase, rent, rating, director, tmdb_url
