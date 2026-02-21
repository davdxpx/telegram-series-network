from tmdbv3api import TMDb, TV, Movie, Season, Episode
from typing import Optional, Dict, List
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class TMDBClient:
    """
    Wrapper around the TMDB API to fetch show metadata.
    """
    def __init__(self, api_key: str):
        self.tmdb = TMDb()
        self.tmdb.api_key = api_key
        self.tmdb.language = "en"
        self.tv_api = TV()
        self.movie_api = Movie()
        self.season_api = Season()
        self.episode_api = Episode()

    def search_tv_show(self, query: str) -> List[Dict]:
        """
        Search for a TV show by name.
        """
        try:
            results = self.tv_api.search(query)
            return [
                {
                    "id": show.id,
                    "name": show.name,
                    "overview": getattr(show, 'overview', ''),
                    "poster_path": getattr(show, 'poster_path', None),
                    "backdrop_path": getattr(show, 'backdrop_path', None),
                    "first_air_date": getattr(show, 'first_air_date', None),
                    "vote_average": getattr(show, 'vote_average', 0.0)
                }
                for show in results
            ]
        except Exception as e:
            logger.error(f"Error searching TMDB for '{query}': {e}")
            return []

    def get_show_details(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get detailed info about a show.
        """
        try:
            show = self.tv_api.details(tmdb_id)
            return {
                "id": show.id,
                "name": show.name,
                "overview": show.overview,
                "poster_path": show.poster_path,
                "backdrop_path": show.backdrop_path,
                "first_air_date": show.first_air_date,
                "vote_average": show.vote_average,
                "number_of_seasons": show.number_of_seasons,
                "status": show.status
            }
        except Exception as e:
            logger.error(f"Error getting details for ID {tmdb_id}: {e}")
            return None

    def get_season_details(self, tmdb_id: int, season_number: int) -> Optional[Dict]:
        """
        Get info about a specific season.
        """
        try:
            season = self.season_api.details(tmdb_id, season_number)
            return {
                "id": season.id,
                "name": season.name,
                "overview": season.overview,
                "poster_path": season.poster_path,
                "air_date": season.air_date,
                "season_number": season.season_number,
                "episodes": [
                    {
                        "episode_number": ep.episode_number,
                        "name": ep.name,
                        "overview": ep.overview,
                        "still_path": ep.still_path,
                        "air_date": ep.air_date,
                        "runtime": getattr(ep, 'runtime', None)
                    }
                    for ep in season.episodes
                ]
            }
        except Exception as e:
            logger.error(f"Error getting season {season_number} for show {tmdb_id}: {e}")
            return None

# Singleton instance
tmdb_client = TMDBClient(settings.TMDB_API_KEY)
