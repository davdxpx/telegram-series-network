import aiohttp
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logging import logger

class AsyncTMDB:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _request(self, endpoint: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        params["api_key"] = self.api_key
        params["language"] = "en-US" # Default to English

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.BASE_URL}{endpoint}", params=params) as response:
                    if response.status != 200:
                        logger.error(f"TMDB Error {response.status}: {await response.text()}")
                        return {}
                    return await response.json()
            except Exception as e:
                logger.error(f"TMDB Request Failed: {e}")
                return {}

    async def search_multi(self, query: str) -> List[Dict[str, Any]]:
        """Search for movies and TV shows."""
        data = await self._request("/search/multi", {"query": query})
        return data.get("results", [])

    async def get_tv_show(self, tmdb_id: int) -> Dict[str, Any]:
        return await self._request(f"/tv/{tmdb_id}")

    async def get_season(self, tv_id: int, season_number: int) -> Dict[str, Any]:
        return await self._request(f"/tv/{tv_id}/season/{season_number}")

    async def get_episode(self, tv_id: int, season_number: int, episode_number: int) -> Dict[str, Any]:
        return await self._request(f"/tv/{tv_id}/season/{season_number}/episode/{episode_number}")

    async def get_movie(self, tmdb_id: int) -> Dict[str, Any]:
        return await self._request(f"/movie/{tmdb_id}")

    def get_image_url(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}{path}"

tmdb_client = AsyncTMDB(settings.TMDB_API_KEY)
