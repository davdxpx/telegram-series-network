from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.models import Network, User
from app.keyboards.inline import storage_channels_keyboard
from app.config import settings
from beanie import PydanticObjectId

router = Router()

# Removed /my_networks and multi-network management logic.
# Now focused on managing the single default network.

async def get_main_network():
    return await Network.find_one({})

@router.message(Command("add_channel"))
async def cmd_add_channel(message: Message):
    # Usage: /add_channel <channel_id>
    if message.from_user.id not in settings.ADMIN_IDS:
        return

    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Usage: /add_channel <channel_id>\n\nAdd the bot as Admin to the channel first!")

    try:
        channel_id = int(args[1])
    except ValueError:
        return await message.answer("Channel ID must be an integer (e.g. -100123456789).")

    network = await get_main_network()
    if not network:
        return await message.answer("Main network not initialized. Run /start first.")

    if channel_id not in network.storage_channel_ids:
        network.storage_channel_ids.append(channel_id)
        await network.save()
        await message.answer(f"✅ Storage Channel `{channel_id}` linked successfully!\n\nAny file uploaded there will now be processed.")
    else:
        await message.answer("Channel is already linked.")

@router.callback_query(F.data.startswith("add_storage_channel:"))
async def cb_add_storage_prompt(callback: CallbackQuery):
    # Only for admins
    if callback.from_user.id not in settings.ADMIN_IDS:
        return await callback.answer("Admin only.", show_alert=True)

    await callback.message.answer(
        f"To add a storage channel:\n"
        f"1. Create a Private Channel.\n"
        f"2. Add me as Admin.\n"
        f"3. Get the Channel ID (e.g. forward a msg to a bot like @userinfobot or check logs).\n"
        f"4. Type `/add_channel <channel_id>` here."
    )
    await callback.answer()
