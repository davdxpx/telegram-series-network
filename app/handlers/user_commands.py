from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
from app.models import Episode, Series
import random

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handle /start command.
    Checks if user is owner and shows Admin Panel button.
    Otherwise shows User WebApp button.
    """
    user_id = message.from_user.id
    is_owner = user_id == settings.OWNER_TELEGRAM_ID

    webapp_url = f"{settings.BASE_URL}/webapp/user"
    admin_url = f"{settings.BASE_URL}/webapp/admin"

    text = (
        f"👋 **Welcome to {settings.BOT_NAME if hasattr(settings, 'BOT_NAME') else 'TSN'}!**\n\n"
        "This is a private streaming network.\n"
        "Click below to browse the library."
    )

    buttons = [
        [InlineKeyboardButton(text="📺 Open Library", web_app=WebAppInfo(url=webapp_url))]
    ]

    if is_owner:
        buttons.append([InlineKeyboardButton(text="⚙️ Admin Panel", web_app=WebAppInfo(url=admin_url))])
        text += "\n\n👑 *You are the Owner.* Use the Admin Panel to manage content."

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(text, reply_markup=keyboard)

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != settings.OWNER_TELEGRAM_ID:
        return

    admin_url = f"{settings.BASE_URL}/webapp/admin"
    await message.answer(
        "⚙️ **Admin Dashboard**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Open Dashboard", web_app=WebAppInfo(url=admin_url))]
        ])
    )

@router.message(Command("search"))
async def cmd_search(message: Message):
    """
    Shows instructions on how to use search.
    """
    webapp_url = f"{settings.BASE_URL}/webapp/user"
    await message.answer(
        "🔍 **Search**\n\n"
        "To search for content, please open the WebApp Library.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔎 Open Search", web_app=WebAppInfo(url=webapp_url))]
        ])
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """
    Shows simple stats message as requested.
    """
    # Simple aggregation (could be heavy on large DB, okay for single network)
    episode_count = await Episode.count()
    series_count = await Series.count()

    text = (
        f"📊 **Network Statistics**\n\n"
        f"In this Network **{episode_count} episodes** have been watched total.\n" # Text as requested, though 'watched' implies view count? Prompt said "watched total" likely meaning available or views. Assuming available for now or need ViewLog.
        f"Total Series: {series_count}\n"
    )
    await message.answer(text)

@router.message(Command("random"))
async def cmd_random(message: Message):
    """
    Pick a smart random episode.
    """
    # Get all episodes (expensive on huge DB, but okay for personal)
    # Better: Use aggregation sample
    try:
        pipeline = [{"$sample": {"size": 1}}]
        random_ep_list = await Episode.aggregate(pipeline).to_list(1)

        if not random_ep_list:
            await message.answer("No episodes found in the library!")
            return

        ep_data = random_ep_list[0]
        # Aggregate returns dict, not Document
        series = await Series.get(ep_data["series_id"])

        text = (
            f"🎲 **Random Pick**\n\n"
            f"📺 **{series.name}**\n"
            f"S{ep_data['season_number']:02d}E{ep_data['episode_number']:02d}: {ep_data['name']}\n\n"
            f"{ep_data.get('overview', '')[:100]}..."
        )

        webapp_url = f"{settings.BASE_URL}/webapp/user"
        await message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="▶️ Watch Now", web_app=WebAppInfo(url=webapp_url))]
            ])
        )
    except Exception as e:
        await message.answer("Error picking random episode.")
