from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from app.models import User, Network
from app.keyboards.inline import start_keyboard, network_management_keyboard
from app.utils.logging import logger
import uuid

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await User.find_one(User.telegram_id == message.from_user.id)
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        await user.create()
        logger.info(f"New user created: {user.telegram_id}")

    await message.answer(
        "👋 Welcome to **Telegram Series Network (TSN)**!\n\n"
        "I can help you build your own private streaming network.\n"
        "Use the menu below to get started.",
        reply_markup=start_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "📚 **TSN Bot Help**\n\n"
        "/start - Main menu\n"
        "/create_network <name> - Create a new network\n"
        "/my_networks - List your networks\n"
        "/stats - View statistics\n"
        "\n"
        "To add content:\n"
        "1. Create a network.\n"
        "2. Add a storage channel to it.\n"
        "3. Upload files to that channel."
    )
    await message.answer(text)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    # Retrieve user stats (mock data for now, will implement real queries)
    # The requirement is: "In your Network 124 episodes have been watched total"

    # We need to find networks owned by user
    user = await User.find_one(User.telegram_id == message.from_user.id)
    if not user:
        return await message.answer("You are not registered. /start")

    networks = await Network.find(Network.owner_id == user.telegram_id).to_list()

    total_networks = len(networks)

    await message.answer(
        f"📊 **Your Statistics**\n\n"
        f"Networks Owned: {total_networks}\n"
        f"In your Network **0 episodes** have been watched total.\n" # Placeholder
        f"Most Active User: You!"
    )

@router.message(Command("create_network"))
async def cmd_create_network(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.answer("Usage: /create_network <Network Name>")

    network_name = args[1]

    # Create Network
    network = Network(
        name=network_name,
        owner_id=message.from_user.id,
        invite_code=str(uuid.uuid4())[:8]
    )
    await network.create()

    await message.answer(
        f"✅ Network **{network_name}** created!\n"
        f"Invite Code: `{network.invite_code}`\n\n"
        f"Next: Add a storage channel with `/add_storage_channel {network.id} <channel_id>`"
    )
