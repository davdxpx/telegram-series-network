from aiogram import Router, F
from aiogram.types import Message
from app.models import StorageChannel, AdminSettings
from app.handlers.batch_import import process_new_file
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.channel_post(F.video | F.document)
async def handle_channel_post(message: Message):
    """
    Listens to new posts in channels.
    If the channel is a registered Storage Channel, trigger the import logic.
    """
    channel_id = message.chat.id

    # 1. Check if this channel is a registered Storage Channel
    storage_channel = await StorageChannel.find_one(StorageChannel.channel_id == channel_id)

    if not storage_channel:
        # Ignore posts from unknown channels
        return

    if not storage_channel.is_active:
        return

    # 2. Check if a Batch Import is currently running for this channel
    # This state is usually stored in Redis or DB.
    # For now, we will just Log it. Implementing full Batch Logic in batch_import.py

    logger.info(f"New file detected in Storage Channel {storage_channel.name} (ID: {channel_id})")

    # Forward to the batch processor
    await process_new_file(message, storage_channel)
