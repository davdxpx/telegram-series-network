from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from typing import List, Optional
from app.config import settings

def start_keyboard() -> InlineKeyboardMarkup:
    # Ensure BASE_URL is set and valid
    if not settings.BASE_URL:
        # Fallback or error state button if not configured
        # But we assume it is set in production
        webapp_url = "https://telegram.org"
    else:
        # Construct the full URL to the static WebApp
        base = settings.BASE_URL.rstrip("/")
        webapp_url = f"{base}/static/index.html"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📺 Open Library", web_app=WebAppInfo(url=webapp_url)),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
        ]
    ])

def confirm_upload_keyboard(file_unique_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm & Save", callback_data=f"confirm_upload:{file_unique_id}"),
            InlineKeyboardButton(text="✏️ Edit Info", callback_data=f"edit_upload:{file_unique_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Discard", callback_data=f"discard_upload:{file_unique_id}"),
        ]
    ])

def storage_channels_keyboard(network_id: str, channels: List[int]) -> InlineKeyboardMarkup:
    buttons = []
    for channel_id in channels:
        buttons.append([InlineKeyboardButton(text=f"Channel {channel_id}", callback_data="noop")])

    buttons.append([InlineKeyboardButton(text="➕ Add Channel", callback_data=f"add_storage_channel:{network_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
