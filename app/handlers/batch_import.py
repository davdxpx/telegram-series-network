from aiogram.types import Message
from app.models import StorageChannel, Bundle, Series, Season, Episode
from app.utils.guessit_parser import MediaParser
from app.utils.tmdb import tmdb_client
from app.config import settings
import logging
import asyncio
from beanie import PydanticObjectId
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# Redis Connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Key Prefix
BATCH_KEY_PREFIX = "batch_import:"

async def get_batch_info(channel_id: int):
    """
    Get active batch info for a channel.
    Returns dict {bundle_id: str} or None
    """
    key = f"{BATCH_KEY_PREFIX}{channel_id}"
    bundle_id = await redis_client.get(key)
    if bundle_id:
        return {"bundle_id": bundle_id}
    return None

async def start_batch(channel_id: int, bundle_id: str):
    key = f"{BATCH_KEY_PREFIX}{channel_id}"
    await redis_client.set(key, bundle_id)
    logger.info(f"Started batch import for channel {channel_id} into bundle {bundle_id}")

async def stop_batch(channel_id: int):
    key = f"{BATCH_KEY_PREFIX}{channel_id}"
    await redis_client.delete(key)
    logger.info(f"Stopped batch import for channel {channel_id}")

async def process_new_file(message: Message, storage_channel: StorageChannel):
    """
    Main logic to process a file:
    1. Check if batch is active.
    2. Parse filename.
    3. Fetch TMDB Metadata.
    4. Create/Get Series, Season.
    5. Create Episode.
    """
    channel_id = message.chat.id

    # Only process if a batch is active for this channel
    batch_info = await get_batch_info(channel_id)
    if not batch_info:
        logger.debug(f"Ignored file in {channel_id}: No active batch.")
        return

    bundle_id = batch_info["bundle_id"]
    try:
        bundle = await Bundle.get(PydanticObjectId(bundle_id))
    except Exception:
        logger.error(f"Invalid bundle ID: {bundle_id}")
        return

    if not bundle:
        logger.error(f"Bundle {bundle_id} not found!")
        return

    # Get file info
    video = message.video or message.document
    if not video:
        return

    file_id = video.file_id
    file_unique_id = video.file_unique_id
    filename = video.file_name or "Unknown_Video.mkv"

    # 1. Parse Filename (CPU bound, run in thread)
    parsed = await asyncio.to_thread(MediaParser.parse_filename, filename)
    if not parsed.get("title"):
        logger.warning(f"Could not parse title from {filename}")
        # TODO: Handle unparsed files (add to 'Unsorted' list)
        return

    show_name = parsed["title"]
    season_num = parsed.get("season", 1)
    episode_num = parsed.get("episode", 1)

    # 2. Search TMDB (Network bound, run in thread)
    results = await asyncio.to_thread(tmdb_client.search_tv_show, show_name)
    if not results:
        logger.warning(f"No TMDB results for {show_name}")
        return

    # Assume first result is correct (Batch Mode)
    # In a real rigorous system, we might ask for confirmation,
    # but for "Batch" we value speed.
    tmdb_show = results[0]
    tmdb_id = tmdb_show["id"]

    # 3. Get/Create Series
    series = await Series.find_one(Series.tmdb_id == tmdb_id)
    if not series:
        details = await asyncio.to_thread(tmdb_client.get_show_details, tmdb_id)
        if not details:
            return

        series = Series(
            tmdb_id=tmdb_id,
            name=details["name"],
            overview=details.get("overview"),
            poster_path=details.get("poster_path"),
            backdrop_path=details.get("backdrop_path"),
            first_air_date=details.get("first_air_date"),
            rating=details.get("vote_average", 0),
            bundle_id=bundle.id
        )
        await series.create()

        # Update Bundle count
        bundle.series_count += 1
        await bundle.save()

    # 4. Get/Create Season
    season = await Season.find_one(Season.series_id == series.id, Season.season_number == season_num)
    if not season:
        season_details = await asyncio.to_thread(tmdb_client.get_season_details, tmdb_id, season_num)
        if not season_details:
             # Fallback if season details fail
            season = Season(
                series_id=series.id,
                season_number=season_num,
                name=f"Season {season_num}",
                episode_count=0
            )
        else:
            season = Season(
                series_id=series.id,
                season_number=season_num,
                name=season_details.get("name", f"Season {season_num}"),
                overview=season_details.get("overview"),
                poster_path=season_details.get("poster_path"),
                air_date=season_details.get("air_date"),
                episode_count=0
            )
        await season.create()

    # 5. Create Episode
    # Check if exists
    existing_ep = await Episode.find_one(Episode.file_unique_id == file_unique_id)
    if existing_ep:
        logger.info(f"Episode {filename} already exists.")
        return

    # Get specific episode details from Season info if available, else generic
    episode_name = f"Episode {episode_num}"
    episode_overview = ""
    episode_still = None

    # Try to fetch episode specific metadata if not already
    # (Optimally we cached the season response, but for now simple)

    new_episode = Episode(
        series_id=series.id,
        season_id=season.id,
        episode_number=episode_num,
        name=episode_name, # TMDB fetch could improve this
        overview=episode_overview,
        still_path=episode_still,
        storage_channel_id=channel_id,
        message_id=message.message_id,
        file_id=file_id,
        file_unique_id=file_unique_id,
        file_size=video.file_size,
        original_filename=filename
    )
    await new_episode.create()

    # Update counts
    season.episode_count += 1
    await season.save()

    logger.info(f"Imported: {series.name} - S{season_num:02d}E{episode_num:02d}")
