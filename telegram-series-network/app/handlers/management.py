from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.models import Network, User
from app.keyboards.inline import network_management_keyboard, storage_channels_keyboard
from beanie import PydanticObjectId

router = Router()

@router.message(Command("my_networks"))
async def cmd_my_networks(message: Message):
    networks = await Network.find(Network.owner_id == message.from_user.id).to_list()

    if not networks:
        return await message.answer("You don't own any networks yet. Use /create_network.")

    for net in networks:
        await message.answer(
            f"🌐 **{net.name}**\n"
            f"Members: {len(net.members)}\n"
            f"Storage Channels: {len(net.storage_channel_ids)}",
            reply_markup=network_management_keyboard(str(net.id))
        )

@router.callback_query(F.data.startswith("manage_storage:"))
async def cb_manage_storage(callback: CallbackQuery):
    network_id = callback.data.split(":")[1]
    network = await Network.get(PydanticObjectId(network_id))

    if not network:
        return await callback.answer("Network not found", show_alert=True)

    if network.owner_id != callback.from_user.id:
        return await callback.answer("You are not the owner", show_alert=True)

    await callback.message.edit_text(
        f"Storage Channels for **{network.name}**:",
        reply_markup=storage_channels_keyboard(network_id, network.storage_channel_ids)
    )

@router.callback_query(F.data.startswith("add_storage_channel:"))
async def cb_add_storage_prompt(callback: CallbackQuery):
    network_id = callback.data.split(":")[1]
    await callback.message.answer(
        f"To add a storage channel:\n"
        f"1. Create a Private Channel.\n"
        f"2. Add me (@{callback.bot.me.username}) as Admin.\n"
        f"3. Forward a message from that channel to me here.\n"
        f"OR type `/register_channel {network_id} <channel_id>` if you know the ID."
    )
    await callback.answer()

@router.message(Command("register_channel"))
async def cmd_register_channel(message: Message):
    # Usage: /register_channel <network_id> <channel_id>
    args = message.text.split()
    if len(args) < 3:
        return await message.answer("Usage: /register_channel <network_id> <channel_id>")

    network_id = args[1]
    try:
        channel_id = int(args[2])
    except ValueError:
        return await message.answer("Channel ID must be an integer.")

    network = await Network.get(PydanticObjectId(network_id))
    if not network:
        return await message.answer("Network not found.")

    if network.owner_id != message.from_user.id:
        return await message.answer("Not authorized.")

    if channel_id not in network.storage_channel_ids:
        network.storage_channel_ids.append(channel_id)
        await network.save()
        await message.answer(f"✅ Channel {channel_id} added to **{network.name}**!")
    else:
        await message.answer("Channel already added.")
