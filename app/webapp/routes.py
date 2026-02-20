from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import Network, Series, Episode
from app.webapp.stream import router as stream_router
from beanie import PydanticObjectId

router = APIRouter()

# Include the stream router
router.include_router(stream_router)

# API Endpoints for the SPA Frontend

@router.get("/api/networks/{user_id}")
async def get_user_networks(user_id: int):
    # Security: Verify via Telegram Login Widget hash ideally.
    # For MVP, we trust the ID passed (in a real app, use initData validation)
    networks = await Network.find(Network.owner_id == user_id).to_list() # Simply owner for now
    return networks

@router.get("/api/network/{network_id}/content")
async def get_network_content(network_id: str):
    # Return list of series
    series = await Series.find(Series.network_id == PydanticObjectId(network_id)).to_list()
    return series

@router.get("/api/series/{series_id}/episodes")
async def get_series_episodes(series_id: str):
    episodes = await Episode.find(Episode.series_id == PydanticObjectId(series_id)).sort("season_id", "episode_number").to_list()
    return episodes

@router.get("/api/episode/{episode_id}")
async def get_episode_details(episode_id: str):
    episode = await Episode.get(PydanticObjectId(episode_id))
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode
