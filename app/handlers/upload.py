from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.models import Network, Episode, Series, Season, User
from app.utils.parser import parse_filename
from app.utils.tmdb import tmdb_client
from app.keyboards.inline import confirm_upload_keyboard
from app.utils.logging import logger
from beanie import PydanticObjectId

router = Router()

# Listen for messages in CHANNELS (Storage Channels)
# We need to check if the channel is a registered storage channel
@router.channel_post(F.video | F.document)
async def handle_channel_upload(message: Message):
    # Check if this channel is registered in any network
    # In production with many networks, we might cache this mapping in Redis
    network = await Network.find_one({"storage_channel_ids": message.chat.id})

    if not network:
        # Not a managed channel, ignore
        return

    file_id = message.video.file_id if message.video else message.document.file_id
    file_unique_id = message.video.file_unique_id if message.video else message.document.file_unique_id
    filename = message.video.file_name if message.video else message.document.file_name

    if not filename:
        filename = message.caption or "unknown_file"

    logger.info(f"New file in storage channel {message.chat.id}: {filename}")

    # Parse Filename
    parsed = parse_filename(filename)
    if not parsed:
        # Could not parse, maybe notify owner if we could?
        # Since bots can't initiate DMs easily without prior interaction, we rely on the owner checking things.
        # Or we reply in the channel if we have permission.
        return

    # Fetch TMDB Data
    # For MVP, assume it's a TV Show episode if Season/Episode detected
    # If not, maybe a movie?
    # Let's simplify: If S/E detected -> TV. Else -> Movie (if requested later)

    series_name = parsed.get("title")
    season_num = parsed.get("season")
    episode_num = parsed.get("episode")

    if series_name and season_num and episode_num:
        # Search TMDB
        results = await tmdb_client.search_multi(series_name)
        if not results:
            logger.warning(f"No TMDB results for {series_name}")
            return

        # Pick first result (MVP)
        show = results[0]
        tmdb_id = show["id"]

        # We need to save this pending confirmation or save directly?
        # Requirement: "Asks the uploader to confirm / assign"
        # Since this is a channel post, we can reply in the channel if allowed,
        # OR we send a message to the Network Owner.

        owner = await User.find_one(User.telegram_id == network.owner_id)
        if owner:
            # Send DM to owner
            # We need to save the file context temporarily. Redis is good for this.
            # But let's create the objects directly and mark as "pending" or just notify.

            # Let's try to notify the owner
            try:
                await message.bot.send_message(
                    chat_id=owner.telegram_id,
                    text=f"📥 **New Upload Detected in {network.name}**\n\n"
                         f"File: `{filename}`\n"
                         f"Detected: **{show['name']}** - S{season_num}E{episode_num}\n\n"
                         f"Please confirm to add to library.",
                    reply_markup=confirm_upload_keyboard(file_unique_id)
                )

                # We need to store the context (file_id, channel_id, message_id, tmdb info)
                # to process the callback.
                # For now, let's just create the Episode but maybe valid=False?
                # Or use Redis.
                # Simplest for this task: Create the Series/Season/Episode structure now!

                # Check/Create Series
                series = await Series.find_one(Series.tmdb_id == tmdb_id, Series.network_id == network.id)
                if not series:
                    series = Series(
                        network_id=network.id,
                        tmdb_id=tmdb_id,
                        title=show["name"],
                        overview=show.get("overview"),
                        poster_path=show.get("poster_path"),
                        backdrop_path=show.get("backdrop_path"),
                        first_air_date=show.get("first_air_date")
                    )
                    await series.create()

                # Check/Create Season
                season = await Season.find_one(Season.series_id == series.id, Season.season_number == season_num)
                if not season:
                    season = Season(
                        series_id=series.id,
                        network_id=network.id,
                        season_number=season_num,
                        name=f"Season {season_num}"
                    )
                    await season.create()

                # Create Episode
                episode = Episode(
                    season_id=season.id,
                    series_id=series.id,
                    network_id=network.id,
                    episode_number=episode_num,
                    file_id=file_id,
                    file_unique_id=file_unique_id,
                    tmdb_id=None # We could fetch specific episode ID later
                )
                await episode.create()

            except Exception as e:
                logger.error(f"Failed to notify owner: {e}")

@router.callback_query(F.data.startswith("confirm_upload:"))
async def cb_confirm_upload(callback: CallbackQuery):
    file_unique_id = callback.data.split(":")[1]

    # Verify the episode exists (created in handler above)
    episode = await Episode.find_one(Episode.file_unique_id == file_unique_id)
    if episode:
        await callback.message.edit_text(f"✅ Episode saved to library!")
    else:
        await callback.message.edit_text("❌ Error: File not found in DB.")
