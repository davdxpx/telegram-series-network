from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from app.models import User, Network
from app.keyboards.inline import start_keyboard
from app.utils.logging import logger
from app.config import settings
import uuid

router = Router()

async def ensure_default_network():
    """Ensure a default network exists for the bot instance."""
    # Check if any network exists
    network = await Network.find_one({})
    if not network:
        if not settings.ADMIN_IDS:
            logger.warning("No ADMIN_IDS set! Cannot create default network owner.")
            return None

        owner_id = settings.ADMIN_IDS[0]
        logger.info(f"Creating default 'Main Network' owned by Admin ID {owner_id}")

        network = Network(
            name="Main Network",
            owner_id=owner_id,
            invite_code=str(uuid.uuid4())[:8]
        )
        await network.create()
    return network

@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"📝 Received /start from User ID: {message.from_user.id}")

    try:
        # Ensure user exists
        user = await User.find_one(User.telegram_id == message.from_user.id)
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )
            await user.create()
            logger.success(f"New user registered: {user.telegram_id}")

        # Ensure default network exists (singleton pattern)
        # In a real scenario, we might do this on startup, but doing it here ensures it's ready when needed
        network = await ensure_default_network()

        # Check if user is owner/admin
        is_admin = message.from_user.id in settings.ADMIN_IDS

        welcome_text = (
            "👋 **Welcome to the Series Network!**\n\n"
            "Stream your private library directly here.\n"
            "Click **Open Library** to start watching."
        )

        if is_admin:
            welcome_text += "\n\n👑 **Admin Controls:**\n" \
                            "/stats - View statistics\n" \
                            "/add_channel <channel_id> - Link a storage channel"

        await message.answer(
            welcome_text,
            reply_markup=start_keyboard()
        )

    except Exception as e:
        logger.error(f"Error in /start handler: {e}")
        await message.answer("⚠️ An error occurred.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "📚 **Help**\n\n"
        "This bot hosts a private media library.\n"
        "Use the **Open Library** button to browse and watch content."
    )
    if message.from_user.id in settings.ADMIN_IDS:
        text += "\n\n**Admin Commands:**\n" \
                "/add_channel <id> - Add a storage channel for uploads.\n" \
                "Simply upload files to that channel to add them."

    await message.answer(text)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return # Ignore non-admins

    # Stats logic...
    await message.answer("📊 Stats placeholder (Implementing real stats soon)")
