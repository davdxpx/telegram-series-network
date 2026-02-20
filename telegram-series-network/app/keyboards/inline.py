from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from typing import List, Optional

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📺 Open Library", web_app=WebAppInfo(url="https://google.com")), # Placeholder URL
        ],
        [
            InlineKeyboardButton(text="➕ Create Network", callback_data="create_network"),
            InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
        ]
    ])

def network_management_keyboard(network_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Manage Members", callback_data=f"manage_members:{network_id}"),
            InlineKeyboardButton(text="📡 Storage Channels", callback_data=f"manage_storage:{network_id}"),
        ],
        [
            InlineKeyboardButton(text="🗑️ Delete Network", callback_data=f"delete_network:{network_id}"),
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
        buttons.append([InlineKeyboardButton(text=f"channel {channel_id}", callback_data="noop")]) # Just listing for now

    buttons.append([InlineKeyboardButton(text="➕ Add Channel", callback_data=f"add_storage_channel:{network_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data=f"manage_network:{network_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
